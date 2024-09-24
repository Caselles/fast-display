import threading
import numpy as np
import cv2
import time
import queue


def image_producer(queue, width, height, stop_event):
    while not stop_event.is_set():
        # Generate a random image
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        queue.put(image)


if __name__ == '__main__':
    width, height = 3000, 3000
    queue = queue.Queue()
    stop_event = threading.Event()
    producer_thread = threading.Thread(
        target=image_producer, args=(queue, width, height, stop_event))
    producer_thread.start()

    # Initialize variables for FPS calculation
    frame_count = 0
    start_time = time.time()
    fps = 0

    while not stop_event.is_set():
        image = queue.get()
        frame_count += 1

        # Calculate FPS every second
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:
            fps = frame_count / elapsed_time
            frame_count = 0
            start_time = time.time()

        # Display FPS on the image
        cv2.putText(image, f'FPS: {fps:.2f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the image
        cv2.imshow('Video Display', image)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    # Cleanup
    cv2.destroyAllWindows()
    producer_thread.join()`
