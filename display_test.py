import multiprocessing as mp
import numpy as np
import glfw
from OpenGL.GL import *
import time


def image_producer(queue, width, height, stop_event):
    while not stop_event.is_set():
        # Generate a random image using NumPy
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        queue.put(image)


def main():
    width, height = 3000, 3000
    queue = mp.Queue()  # Limit queue size to prevent memory overflow
    stop_event = mp.Event()
    producer_process = mp.Process(
        target=image_producer, args=(queue, width, height, stop_event))
    producer_process.start()

    # Initialize GLFW and create a window
    if not glfw.init():
        return
    window = glfw.create_window(3000, 3000, "Video Display", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    # OpenGL settings
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)

    frame_count = 0
    start_time = time.time()
    fps = 0

    while not stop_event.is_set() and not glfw.window_should_close(window):
        if not queue.empty():
            image = queue.get()
            frame_count += 1

            # Calculate FPS every second
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = frame_count / elapsed_time
                frame_count = 0
                start_time = time.time()
                print(f"FPS: {fps:.2f}")

            # Bind texture
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                         0, GL_RGB, GL_UNSIGNED_BYTE, image)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Render textured quad
            glClear(GL_COLOR_BUFFER_BIT)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(-1, -1)
            glTexCoord2f(1, 0)
            glVertex2f(1, -1)
            glTexCoord2f(1, 1)
            glVertex2f(1, 1)
            glTexCoord2f(0, 1)
            glVertex2f(-1, 1)
            glEnd()

            glfw.swap_buffers(window)
            glfw.poll_events()
        else:
            # Sleep briefly to prevent busy waiting
            time.sleep(0.001)

        # Check for 'q' key press to exit
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            stop_event.set()

    # Cleanup
    stop_event.set()
    producer_process.join()
    glDeleteTextures([texture_id])
    glfw.terminate()


if __name__ == '__main__':
    main()
