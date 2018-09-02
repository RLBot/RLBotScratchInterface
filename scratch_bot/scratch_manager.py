import asyncio
import json
from datetime import datetime, timedelta

import flatbuffers
import websockets
from rlbot.botmanager.bot_helper_process import BotHelperProcess
from rlbot.messages.flat import GameTickPacket, ControllerState, PlayerInput, TinyPacket, TinyPlayer, Vector3, Rotator, \
    TinyBall
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import GameInterface

PORT = 42008
MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0)


class ScratchManager(BotHelperProcess):

    def __init__(self, agent_metadata_queue, quit_event):
        super().__init__(agent_metadata_queue, quit_event)
        self.logger = get_logger('scratch_mgr')
        self.game_interface = GameInterface(self.logger)
        self.current_sockets = set()

    async def data_exchange(self, websocket, path):
        async for message in websocket:
            controller_states = json.loads(message)

            for key, scratch_state in controller_states.items():
                self.game_interface.update_player_input_flat(self.convert_to_flatbuffer(scratch_state, int(key)))

            self.current_sockets.add(websocket)

    def start(self):
        self.logger.info("Starting scratch manager")

        self.game_interface.load_interface()

        asyncio.get_event_loop().run_until_complete(websockets.serve(self.data_exchange, port=PORT))
        asyncio.get_event_loop().run_until_complete(self.game_loop())

    async def game_loop(self):

        last_tick_game_time = None  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent

        # Run until main process tells to stop
        while not self.quit_event.is_set():
            before = datetime.now()

            game_tick_flat_binary = self.game_interface.get_live_data_flat_binary()
            if game_tick_flat_binary is None:
                continue

            game_tick_flat = GameTickPacket.GameTickPacket.GetRootAsGameTickPacket(game_tick_flat_binary, 0)

            # Run the Agent only if the gameInfo has updated.
            tick_game_time = self.get_game_time(game_tick_flat)
            worth_communicating = tick_game_time != last_tick_game_time or \
                                  datetime.now() - last_call_real_time >= MAX_AGENT_CALL_PERIOD

            ball = game_tick_flat.Ball()
            if ball is not None and worth_communicating:
                last_tick_game_time = tick_game_time
                last_call_real_time = datetime.now()

                tiny_player_offsets = []
                builder = flatbuffers.Builder(0)

                for i in range(game_tick_flat.PlayersLength()):
                    tiny_player_offsets.append(copy_player(game_tick_flat.Players(i), builder))

                TinyPacket.TinyPacketStartPlayersVector(builder, game_tick_flat.PlayersLength())
                for i in reversed(range(0, len(tiny_player_offsets))):
                    builder.PrependUOffsetTRelative(tiny_player_offsets[i])
                players_offset = builder.EndVector(len(tiny_player_offsets))

                ballOffset = copy_ball(ball, builder)

                TinyPacket.TinyPacketStart(builder)
                TinyPacket.TinyPacketAddPlayers(builder, players_offset)
                TinyPacket.TinyPacketAddBall(builder, ballOffset)
                packet_offset = TinyPacket.TinyPacketEnd(builder)

                builder.Finish(packet_offset)
                buffer = bytes(builder.Output())

                filtered_sockets = {s for s in self.current_sockets if s.open}
                for socket in filtered_sockets:
                    await socket.send(buffer)

                self.current_sockets = filtered_sockets

            after = datetime.now()
            duration = (after - before).total_seconds()

            sleep_secs = 1 / 60 - duration
            if sleep_secs > 0:
                await asyncio.sleep(sleep_secs)

    def get_game_time(self, game_tick_flat):
        try:
            return game_tick_flat.GameInfo().SecondsElapsed()
        except AttributeError:
            return 0.0

    def convert_to_flatbuffer(self, json_state: dict, index: int):
        builder = flatbuffers.Builder(0)

        ControllerState.ControllerStateStart(builder)
        ControllerState.ControllerStateAddSteer(builder, json_state['steer'])
        ControllerState.ControllerStateAddThrottle(builder, json_state['throttle'])
        ControllerState.ControllerStateAddPitch(builder, json_state['pitch'])
        ControllerState.ControllerStateAddYaw(builder, json_state['yaw'])
        ControllerState.ControllerStateAddRoll(builder, json_state['roll'])
        ControllerState.ControllerStateAddJump(builder, json_state['jump'])
        ControllerState.ControllerStateAddBoost(builder, json_state['boost'])
        ControllerState.ControllerStateAddHandbrake(builder, json_state['handbrake'])
        controller_state = ControllerState.ControllerStateEnd(builder)

        PlayerInput.PlayerInputStart(builder)
        PlayerInput.PlayerInputAddPlayerIndex(builder, index)
        PlayerInput.PlayerInputAddControllerState(builder, controller_state)
        player_input = PlayerInput.PlayerInputEnd(builder)

        builder.Finish(player_input)
        return builder

def copy_v3(v3, builder):
    return Vector3.CreateVector3(builder, v3.X(), v3.Y(), v3.Z())

def copy_rot(rot, builder):
    return Rotator.CreateRotator(builder, rot.Pitch(), rot.Yaw(), rot.Roll())

def copy_player(player, builder):
    TinyPlayer.TinyPlayerStart(builder)
    TinyPlayer.TinyPlayerAddLocation(builder, copy_v3(player.Physics().Location(), builder))
    TinyPlayer.TinyPlayerAddVelocity(builder, copy_v3(player.Physics().Velocity(), builder))
    TinyPlayer.TinyPlayerAddRotation(builder, copy_rot(player.Physics().Rotation(), builder))
    TinyPlayer.TinyPlayerAddTeam(builder, player.Team())
    TinyPlayer.TinyPlayerAddBoost(builder, player.Boost())
    return TinyPlayer.TinyPlayerEnd(builder)

def copy_ball(ball, builder):
    phys = ball.Physics()
    TinyBall.TinyBallStart(builder)
    TinyBall.TinyBallAddLocation(builder, copy_v3(phys.Location(), builder))
    TinyBall.TinyBallAddVelocity(builder, copy_v3(phys.Velocity(), builder))
    return TinyBall.TinyBallEnd(builder)


