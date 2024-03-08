import os
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import shutil
import tempfile

tmp = tempfile.gettempdir()

def stretch_speechbuble(original_path: str, queue) -> Image:
    global tmp
    queue.put('[DEBUG] Function speechbubble.stretch_speechbuble called')
    speechbubble_image = Image.open(os.path.join(os.getcwd(), 'resources/speechbubble.png'))
    original_image = Image.open(original_path)

    #wtf rario twitter
    width_ratio = original_image.width / speechbubble_image.width

    new_width = original_image.width
    new_height = int(speechbubble_image.height * width_ratio)
    resized_speechbubble_image = speechbubble_image.resize((new_width, new_height))

    queue.put('[DEBUG] Function speechbubble.stretch_speechbuble successful')
    return resized_speechbubble_image

def process_image(original_path: str, output_path: str, queue) -> str:
    queue.put('[DEBUG] Function speechbubble.process_image called')

    original_image = Image.open(original_path)
    speechbubble_image = stretch_speechbuble(original_path, queue)

    combined_height = speechbubble_image.height + original_image.height
    combined_width = original_image.width
    new_image = Image.new('RGBA', (combined_width, combined_height))

    new_image.paste(speechbubble_image, (0,  0))
    new_image.paste(original_image, (0, speechbubble_image.height))

    new_image.save(output_path)

    queue.put(f'[DEBUG] Function speechbubble.process_image successful')


# i have no fucking idea how this works
# chatgpt fixed my shitty code
def process_animated_gif(original_path, output_path, queue):
    queue.put('[DEBUG] Function process_animated_gif called')
    frames = []
    delays = []

    queue.put('[DEBUG] Function speechbubble.process_animated_gif: Extracting frames and their delays into an array')
    with Image.open(original_path) as original_image:
        # Extract frames and delays
        for i, frame in enumerate(ImageSequence.Iterator(original_image)):
            frames.append(frame.convert("RGBA"))  # Convert frames to RGBA for transparency support
            try:
                delays.append(frame.info["duration"])  # Extract delay for each frame
            except KeyError:
                delays.append(100)  # Default delay if not specified

    speechbubble_image = stretch_speechbuble(original_path, queue)
    processed_frames = []

    queue.put('[DEBUG] Function speechbubble.process_animated_gif: Applying speechbubble to each frame')
    for frame in frames:
        new_frame = Image.new('RGBA', (original_image.width, original_image.height + speechbubble_image.height))
        new_frame.paste(speechbubble_image, (0, 0))
        new_frame.paste(frame, (0, speechbubble_image.height))
        processed_frames.append(new_frame)

    queue.put('[DEBUG] Function speechbubble.process_animated_gif: Saving processed frames as PNGs')
    temp_dir = os.path.join(tmp, "processed_frames")
    os.makedirs(temp_dir, exist_ok=True)
    frame_paths = []

    for i, frame in enumerate(processed_frames):
        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
        frame.save(frame_path)
        frame_paths.append(frame_path)

    queue.put('[DEBUG] Function speechbubble.process_animated_gif: Combining processed frames into a GIF')
    images = [Image.open(frame_path) for frame_path in frame_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:], duration=delays, loop=0)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    queue.put('[DEBUG] Function speechbubble.process_animated_gif successful')