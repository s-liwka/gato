import os
import pyvips
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import shutil
import tempfile

# making them async is useless

tmp = tempfile.gettempdir()

def generate_caption_image(captions: str, original_image: pyvips.Image, queue) -> str:
    queue.put(f'[DEBUG] Function generate_caption_image called with captions "{captions}"')
    fontsize = original_image.width / 10 # Adjust the divisor as needed
    textwidth = original_image.width * .92
    # stolen from mediaforge ez
    out = pyvips.Image.text(
        captions,
        font=f"Twemoji Color Emoji,FuturaExtraBlackCondensed {fontsize}px",
        rgba=True,
        fontfile=os.path.join(os.getcwd(), "resources/caption.otf"),
        align=pyvips.Align.CENTRE,
        width=textwidth
    )

    out = out.composite((255, 255, 255, 255), mode=pyvips.BlendMode.DEST_OVER)
    out = out.gravity(pyvips.CompassDirection.CENTRE, original_image.width, out.height + fontsize, extend=pyvips.Extend.WHITE)
    out.write_to_file(os.path.join(tmp, 'caption.png'))
    queue.put(f'[DEBUG] Function generate_caption_image successful')
    return os.path.join(tmp, 'caption.png')

def process_image(original_image: str, caption_image: str, output_path: str, queue) -> str:
    global tmp
    queue.put('[DEBUG]  Function captions.process_image called')

    caption_image = Image.open(caption_image)
    original_image = Image.open(original_image)
    
    combined_height = caption_image.height + original_image.height
    combined_width = original_image.width
    new_image = Image.new('RGBA', (combined_width, combined_height))

    new_image.paste(caption_image, (0,  0))
    new_image.paste(original_image, (0, caption_image.height))

    new_image.save(output_path)

    queue.put(f'[DEBUG]  Function captions.process_image successful')


# i have no fucking idea how this works
# chatgpt fixed my shitty code
def process_animated_gif(original_path, caption_path, output_path, queue):
    global tmp
    queue.put('[DEBUG]  Function process_animated_gif called')
    frames = []
    delays = []

    queue.put('[DEBUG]  Function process_animated_gif: Extracting frames and their delays into an array')
    with Image.open(original_path) as original_image:
        # Extract frames and delays
        for i, frame in enumerate(ImageSequence.Iterator(original_image)):
            frames.append(frame.convert("RGBA"))  # Convert frames to RGBA for transparency support
            try:
                delays.append(frame.info["duration"])  # Extract delay for each frame
            except KeyError:
                delays.append(100)  # Default delay if not specified

    caption_image = Image.open(caption_path)
    processed_frames = []

    queue.put('[DEBUG]  Function process_animated_gif: Applying caption to each frame')
    for frame in frames:
        new_frame = Image.new('RGBA', (original_image.width, original_image.height + caption_image.height))
        new_frame.paste(caption_image, (0, 0))
        new_frame.paste(frame, (0, caption_image.height))
        processed_frames.append(new_frame)

    queue.put('[DEBUG]  Function process_animated_gif: Saving processed frames as PNGs')
    temp_dir = os.path.join(tmp, "processed_frames")
    os.makedirs(temp_dir, exist_ok=True)
    frame_paths = []

    for i, frame in enumerate(processed_frames):
        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
        frame.save(frame_path)
        frame_paths.append(frame_path)

    queue.put('[DEBUG]  Function process_animated_gif: Combining processed frames into a GIF')
    images = [Image.open(frame_path) for frame_path in frame_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:], duration=delays, loop=0)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    queue.put('[DEBUG]  Function process_animated_gif successful')
