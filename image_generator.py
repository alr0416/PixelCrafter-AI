import os
import threading
import time
import requests
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageOps
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import json



# Load environment variables
load_dotenv()




def open_minecraft():
    """Opens Minecraft Launcher on Windows."""
    try:
        minecraft_path = os.getenv("MINECRAFT_LAUNCHER_PATH")  # Default path
        subprocess.Popen(minecraft_path)  # Open the launcher
    except Exception as e:
        print(f"Error opening Minecraft: {e}")



def create_function_directory():
    """Gets the world save path from an environment variable, creates necessary subdirectories,
    writes pack.mcmeta, and sets MINECRAFT_FUNCTION_PATH to the function directory.
    """
    # Get the full world path from an environment variable
    world_path = os.getenv('MINECRAFT_WORLD_PATH')

    if not world_path:
        print("Error: MINECRAFT_WORLD_PATH environment variable is not set.")
        return

    if not os.path.exists(world_path):
        print(f"Error: The specified world path does not exist: {world_path}")
        return

    # Define the function directory inside the world
    function_directory = os.path.join(world_path, "datapacks", "ai", "data", "aibuild", "function")

    # Define the pack.mcmeta file path
    pack_mcmeta_path = os.path.join(world_path, "datapacks", "ai", "pack.mcmeta")

    # Create the necessary subdirectories
    os.makedirs(function_directory, exist_ok=True)

    # Create the pack.mcmeta file
    pack_metadata = {
        "pack": {
            "pack_format": 61,
            "description": "AI Build Datapack"
        }
    }

    try:
        with open(pack_mcmeta_path, "w") as f:
            json.dump(pack_metadata, f, indent=4)
        print(f"Created pack.mcmeta at: {pack_mcmeta_path}")

    except Exception as e:
        print(f"Error writing pack.mcmeta: {e}")
        return

    # Set environment variable for the function path
    os.environ["MINECRAFT_FUNCTION_PATH"] = function_directory
    print(f"Set MINECRAFT_FUNCTION_PATH to: {function_directory}")




def capture_input():

    """Handles the image generation process when the user submits a prompt."""
    user_input = entry.get()
    print(f"User Input: {user_input}")

    # Disable "Generate Image" button while generating
    submit_button.config(state=tk.DISABLED)
    image_label.config(image=None)
    image_label.image = None  # Important: Remove reference to free memory
    download_button.pack_forget()
    proceed_button.pack_forget()

    # Show loading animation while generating the image
    response_field.config(text="Generating image...", fg="white")
    start_loading_animation()

    # Run image generation in a separate thread to keep the UI responsive
    threading.Thread(target=generate_image, args=(user_input,), daemon=True).start()

def start_loading_animation():
    """Displays an animated '...' while the image is being generated."""
    def animate():
        dots = ["", ".", "..", "..."]
        i = 0
        while loading:
            response_field.config(text=f"Generating image{dots[i]}", fg="white")
            i = (i + 1) % len(dots)
            time.sleep(0.5)

    global loading
    loading = True
    threading.Thread(target=animate, daemon=True).start()

def setup_gui():
    """Sets up the graphical user interface (GUI) for the AI image generator."""
    global root, image_label, response_field, download_button, proceed_button, submit_button, entry, launch_button



    root = tk.Tk()
    root.title("AI Image Generator")
    root.attributes('-fullscreen', True)  # Open in full-screen mode
    root.configure(bg="#2C2F33")  # Dark background

    # Close Button (Escape full screen)
    close_button = tk.Button(root, text="Exit", font=("Arial", 12, "bold"), bg="red", fg="white",
                             padx=15, pady=5, borderwidth=3, command=root.destroy, cursor="hand2")
    close_button.pack(pady=10, anchor="ne", padx=20)

    # Label
    label = tk.Label(root, text="Enter image description:", font=("Arial", 16, "bold"),
                     fg="white", bg="#2C2F33")
    label.pack(pady=10)

    # Textbox (Entry Widget)
    entry = tk.Entry(root, width=70, font=("Arial", 14), cursor="xterm")
    entry.pack(pady=10, ipady=8)

    # Submit Button (Modern Styling)
    submit_button = tk.Button(root, text="Generate Image", font=("Arial", 14, "bold"),
                              bg="#7289DA", fg="white", padx=25, pady=10, borderwidth=3,
                              relief="ridge", command=capture_input, cursor="hand2")
    submit_button.pack(pady=15)

    # Response Output Field (For Error Messages)
    response_field = tk.Label(root, text="",
                              font=("Arial", 14), fg="white", bg="#2C2F33",
                              wraplength=800, justify="center")
    response_field.pack(pady=10)

    # Image Display Area
    image_label = tk.Label(root, bg="#2C2F33")
    image_label.pack(pady=10)

    # Confirmation Buttons (Initially Hidden)
    button_style = {"font": ("Arial", 14, "bold"), "padx": 25, "pady": 10, "borderwidth": 3, "relief": "ridge", "cursor": "hand2"}

    proceed_button = tk.Button(root, text="Proceed", bg="green", fg="white",
                               command=proceed_with_conversion, **button_style)
    proceed_button.pack(pady=10)
    proceed_button.pack_forget()

    # Download Button (Never Disabled)
    download_button = tk.Button(root, text="Download Image", bg="#43B581", fg="white",
                                command=download_image, **button_style)
    download_button.pack(pady=10)
    download_button.pack_forget()

    launch_button = tk.Button(root, text="Open Minecraft", command=open_minecraft)
    launch_button.pack(pady=20)
    launch_button.pack_forget()


    # Run the GUI
    root.mainloop()

def generate_image(user_input):
    """Generates an image using OpenAI's DALL·E and displays it, but does NOT download."""
    global loading
    client = OpenAI(api_key=os.getenv("KEY"))

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=user_input,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"Image generated: {image_url}")

        loading = False  # Stop the loading animation

        # Display the generated image
        display_image_from_url(image_url)

        submit_button.config(state=tk.NORMAL)


    except Exception as e:
        loading = False
        error_message = f"Error generating image: {e}"
        print(error_message)
        response_field.config(text=error_message, fg="red")
        submit_button.config(state=tk.NORMAL)


def display_image_from_url(image_url):
    """Displays an image in the GUI from a URL (without downloading)."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw)
        img.thumbnail((300, 300))
        img_tk = ImageTk.PhotoImage(img)

        # Update image label
        image_label.config(image=img_tk)
        image_label.image = img_tk

        # Re-enable "Generate Image" button after image is generated
        submit_button.config(state=tk.NORMAL)

        # Show user options after displaying the image
        response_field.config(text="Do you want to proceed?", fg="white")

        # Enable and show Proceed + Download buttons
        proceed_button.config(state=tk.NORMAL)
        proceed_button.pack()
        download_button.pack()

        # Store image URL for later download
        download_button.image_url = image_url

    except Exception as e:
        print(f"Error displaying image: {e}")
        response_field.config(text="Failed to display image.", fg="red")

def proceed_with_conversion():
    """Downloads the generated image into the project folder before processing it."""
    image_url = getattr(download_button, "image_url", None)



    if not image_url:
        response_field.config(text="No image to process!", fg="red")
        return

    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Save image in project folder as "ai_image.png"
        save_path = "ai_image.png"
        with open(save_path, "wb") as f:
            f.write(response.content)

        response_field.config(text="Image saved in project folder! Proceeding with conversion...", fg="green")
        print(f"Image saved to: {save_path}")

        # Process image for Minecraft conversion
        pixels = process_image(save_path)


        if pixels is not None:
            block_grid = convert_pixels_to_blocks(pixels)
            generate_mcfunction(block_grid)
            response_field.config(text="Minecraft function file generated!\nUse /reload and /function build_structure in-game.", fg="green")

            # Add a button to open Minecraft
            launch_button.pack()

        else:
            response_field.config(text="Image processing failed.", fg="red")

    except Exception as e:
        response_field.config(text=f"Error saving image: {e}", fg="red")


def download_image():
    """Saves the generated image into the user's Downloads folder."""
    image_url = getattr(download_button, "image_url", None)
    if not image_url:
        response_field.config(text="No image to download!", fg="red")
        return

    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Save to user's Downloads folder
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        save_path = os.path.join(downloads_folder, "ai_image.png")

        with open(save_path, "wb") as f:
            f.write(response.content)

        response_field.config(text="Image downloaded to your Downloads folder!", fg="green")
        print(f"Image saved to: {save_path}")

    except Exception as e:
        response_field.config(text=f"Error downloading image: {e}", fg="red")























def process_image(image_path, size=(256, 256)):
    """Resizes an image to a square while preserving aspect ratio and converting it to an RGB pixel array."""
    try:
        image = Image.open(image_path).convert("RGB")

        # Ensure the image is square by padding
        image = ImageOps.pad(image, size, method=Image.Resampling.LANCZOS)

        return np.array(image)  # RGB Pixel Array

    except Exception as e:
        print(f"Error processing image: {e}")
        return None











def euclidean_distance(color1, color2):
    """Computes the Euclidean distance between two RGB colors (avoiding overflow)."""
    return np.sqrt(sum((int(c1) - int(c2)) ** 2 for c1, c2 in zip(color1, color2)))


def closest_minecraft_block(rgb):
    """Finds the closest Minecraft block by calculating Euclidean distance."""

    # Define Minecraft block colors (RGB values)
    MINECRAFT_BLOCKS = {
        # Wool Blocks
        "white_wool": (255, 255, 255),
        "light_gray_wool": (200, 200, 200),
        "gray_wool": (100, 100, 100),
        "black_wool": (0, 0, 0),
        "red_wool": (255, 0, 0),
        "orange_wool": (255, 165, 0),
        "yellow_wool": (255, 255, 0),
        "lime_wool": (191, 255, 0),
        "green_wool": (0, 255, 0),
        "cyan_wool": (0, 255, 255),
        "light_blue_wool": (173, 216, 230),
        "blue_wool": (0, 0, 255),
        "purple_wool": (128, 0, 128),
        "magenta_wool": (255, 0, 255),
        "pink_wool": (255, 182, 193),
        "brown_wool": (139, 69, 19),

        # Concrete Blocks
        "white_concrete": (207, 213, 214),
        "light_gray_concrete": (125, 125, 115),
        "gray_concrete": (55, 55, 55),
        "black_concrete": (10, 10, 10),
        "red_concrete": (142, 32, 32),
        "orange_concrete": (224, 97, 0),
        "yellow_concrete": (247, 213, 0),
        "lime_concrete": (127, 204, 25),
        "green_concrete": (102, 127, 51),
        "cyan_concrete": (21, 137, 145),
        "light_blue_concrete": (74, 181, 214),
        "blue_concrete": (37, 49, 146),
        "purple_concrete": (100, 31, 156),
        "magenta_concrete": (169, 48, 159),
        "pink_concrete": (214, 101, 143),
        "brown_concrete": (96, 60, 32),

        # Terracotta Blocks
        "white_terracotta": (209, 178, 161),
        "light_gray_terracotta": (135, 107, 98),
        "gray_terracotta": (85, 61, 54),
        "black_terracotta": (37, 23, 16),
        "red_terracotta": (143, 33, 33),
        "orange_terracotta": (162, 84, 38),
        "yellow_terracotta": (186, 133, 35),
        "lime_terracotta": (103, 117, 52),
        "green_terracotta": (76, 83, 42),
        "cyan_terracotta": (76, 89, 91),
        "light_blue_terracotta": (113, 108, 137),
        "blue_terracotta": (74, 59, 91),
        "purple_terracotta": (118, 70, 86),
        "magenta_terracotta": (149, 87, 108),
        "pink_terracotta": (191, 103, 102),
        "brown_terracotta": (77, 51, 35),

        # Natural Blocks
        "sandstone": (237, 201, 175),
        "smooth_sandstone": (240, 228, 197),
        "red_sandstone": (192, 102, 36),
        "stone": (125, 125, 125),
        "cobblestone": (113, 113, 113),
        "mossy_cobblestone": (100, 117, 100),
        "andesite": (136, 136, 136),
        "diorite": (188, 188, 188),
        "granite": (151, 109, 77),
        "grass_block": (127, 178, 56),
        "dirt": (134, 96, 67),
        "coarse_dirt": (120, 85, 60),
        "podzol": (100, 75, 50),

        # Wood Blocks
        "oak_planks": (162, 130, 78),
        "spruce_planks": (116, 85, 59),
        "birch_planks": (193, 174, 127),
        "jungle_planks": (154, 111, 77),
        "acacia_planks": (167, 92, 51),
        "dark_oak_planks": (102, 78, 52),

        # Other Blocks
        "netherrack": (99, 36, 36),
        "nether_bricks": (46, 23, 28),
        "red_nether_bricks": (95, 18, 22),
        "end_stone": (219, 219, 164),
        "purpur_block": (170, 126, 170),
        "obsidian": (25, 9, 43),
        "glowstone": (249, 220, 92),
        "sea_lantern": (172, 217, 211),
        "prismarine": (99, 163, 140),
        "dark_prismarine": (50, 92, 82),
        "prismarine_bricks": (57, 180, 175),
    }

    return min(MINECRAFT_BLOCKS, key=lambda block: euclidean_distance(rgb, MINECRAFT_BLOCKS[block]))

def convert_pixels_to_blocks(pixel_array):
    """Converts an RGB pixel array into a Minecraft block grid."""
    height, width, _ = pixel_array.shape
    block_grid = []

    for y in range(height):
        row = []
        for x in range(width):
            rgb = tuple(pixel_array[y, x])  # Extract RGB color
            block_name = closest_minecraft_block(rgb)  # Find closest block
            row.append(block_name)
        block_grid.append(row)

    return block_grid #an array of provided block names



# Define the path where the .mcfunction file should be saved

def generate_mcfunction(block_grid):
    """Generates an .mcfunction file for a vertical image that appears a few blocks in front of the player."""
    MINECRAFT_FUNCTION_PATH = os.getenv("MINECRAFT_FUNCTION_PATH")

    if not MINECRAFT_FUNCTION_PATH:
        print("Error: MINECRAFT_FUNCTION_PATH is not set.")
        return

    # Ensure the functions directory exists
    os.makedirs(MINECRAFT_FUNCTION_PATH, exist_ok=True)

    # Define the full file path for the .mcfunction file
    mcfunction_file = os.path.join(MINECRAFT_FUNCTION_PATH, "build_structure.mcfunction")

    try:
        commands = []
        height = len(block_grid)

        # Iterate normally, but flip Y-coordinate placement
        for y, row in enumerate(block_grid):  # Y-axis (height)
            for x, block in enumerate(row):  # X-axis (width)
                commands.append(f"setblock ~3 ~{height - y} ~{x} minecraft:{block}")  # Flip Y positioning

        # Write to the .mcfunction file
        with open(mcfunction_file, "w") as f:
            f.write("\n".join(commands))

        print(f".mcfunction file saved to: {mcfunction_file}")

    except Exception as e:
        print(f"Error writing .mcfunction file: {e}")









def main():
    """Main function to generate, process, and convert the image into a Minecraft build."""


    create_function_directory()
    setup_gui()




if __name__ == "__main__":
    main()
