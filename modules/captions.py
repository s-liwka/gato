import os
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import shutil
import tempfile
import textwrap

# making them async is useless

tmp = tempfile.gettempdir()


def generate_caption_image(captions: str, original_image: Image) -> str:
    print(f'[DEBUG] Function generate_caption_image called with captions "{captions}"')
    fontsize = original_image.width // 10 # Adjust the divisor as needed
    max_chars_per_line = int(fontsize * 0.92)
    lines = textwrap.wrap(captions, width=max_chars_per_line)

    # Calculate the total height needed for all lines
    total_height = len(lines) * fontsize * 1.5 # Adjust the multiplier as needed
    out = Image.new('RGBA', (original_image.width, int(total_height)), (255, 255, 255, 255))
    draw = ImageDraw.Draw(out)

    # Load the font (adjust the path as necessary)
    font = ImageFont.truetype(os.path.join(os.getcwd(), "resources/caption.otf"), fontsize)

    # Draw each line of the caption
    y_text = 0
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        position = ((original_image.width - text_width) // 2, y_text)
        draw.text(position, line, font=font, fill=(0, 0, 0, 255))
        y_text += text_height * 1.5

    # Save the image to a temporary file
    out_path = os.path.join(tmp, 'caption.png')
    out.save(out_path)
    print(f'[DEBUG] Function generate_caption_image successful')
    return out_path


def process_image(original_image: str, caption_image: str, output_path: str) -> str:
    global tmp
    print('[DEBUG]  Function captions.process_image called')

    caption_image = Image.open(caption_image)
    original_image = Image.open(original_image)
    
    combined_height = caption_image.height + original_image.height
    combined_width = original_image.width
    new_image = Image.new('RGBA', (combined_width, combined_height))

    new_image.paste(caption_image, (0,  0))
    new_image.paste(original_image, (0, caption_image.height))

    new_image.save(output_path)

    print(f'[DEBUG]  Function captions.process_image successful')


# i have no fucking idea how this works
# chatgpt fixed my shitty code
def process_animated_gif(original_path, caption_path, output_path):
    global tmp
    print('[DEBUG]  Function process_animated_gif called')
    frames = []
    delays = []

    print('[DEBUG]  Function process_animated_gif: Extracting frames and their delays into an array')
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

    print('[DEBUG]  Function process_animated_gif: Applying caption to each frame')
    for frame in frames:
        new_frame = Image.new('RGBA', (original_image.width, original_image.height + caption_image.height))
        new_frame.paste(caption_image, (0, 0))
        new_frame.paste(frame, (0, caption_image.height))
        processed_frames.append(new_frame)

    print('[DEBUG]  Function process_animated_gif: Saving processed frames as PNGs')
    temp_dir = os.path.join(tmp, "processed_frames")
    os.makedirs(temp_dir, exist_ok=True)
    frame_paths = []

    for i, frame in enumerate(processed_frames):
        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
        frame.save(frame_path)
        frame_paths.append(frame_path)

    print('[DEBUG]  Function process_animated_gif: Combining processed frames into a GIF')
    images = [Image.open(frame_path) for frame_path in frame_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:], duration=delays, loop=0)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    print('[DEBUG]  Function process_animated_gif successful')
