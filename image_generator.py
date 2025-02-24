import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk



# Load environment variables
load_dotenv()



def capture_input():
    user_input = entry.get()
    print(f"User Input: {user_input}")  # Captures and prints the input string

    image_path = generate_image(user_input)

    if image_path:
        # Don't process image yet, wait for user confirmation
        show_confirmation_buttons()



def setup_gui():
    global root, image_label, response_field, download_button, regenerate_button, proceed_button

    root = tk.Tk()
    root.title("AI Image Generator")
    root.attributes('-fullscreen', True)  # Open in full-screen mode
    root.configure(bg="#2C2F33")  # Dark background

    # Close Button (Escape full screen)
    close_button = tk.Button(root, text="Exit", font=("Arial", 12, "bold"), bg="red", fg="white",
                             padx=15, pady=5, borderwidth=3, command=root.destroy)
    close_button.pack(pady=10, anchor="ne", padx=20)

    # Label
    label = tk.Label(root, text="Enter image description:", font=("Arial", 16, "bold"),
                     fg="white", bg="#2C2F33")
    label.pack(pady=10)

    # Textbox (Entry Widget)
    global entry
    entry = tk.Entry(root, width=70, font=("Arial", 14))
    entry.pack(pady=10, ipady=8)

    # Submit Button (Modern Styling)
    submit_button = tk.Button(root, text="Generate Image", font=("Arial", 14, "bold"),
                              bg="#7289DA", fg="white", padx=25, pady=10, borderwidth=3,
                              relief="ridge", command=capture_input)
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
    button_style = {"font": ("Arial", 14, "bold"), "padx": 25, "pady": 10, "borderwidth": 3, "relief": "ridge"}

    regenerate_button = tk.Button(root, text="Regenerate", bg="red", fg="white",
                                  command=capture_input, **button_style)
    regenerate_button.pack(pady=10)
    regenerate_button.pack_forget()

    proceed_button = tk.Button(root, text="Proceed", bg="green", fg="white",
                               command=proceed_with_conversion, **button_style)
    proceed_button.pack(pady=10)
    proceed_button.pack_forget()

    # Download Button (Initially Hidden)
    download_button = tk.Button(root, text="Download Image", bg="#43B581", fg="white",
                                command=download_image, **button_style)
    download_button.pack(pady=10)
    download_button.pack_forget()

    # Run the GUI
    root.mainloop()


def generate_image(user_input, save_path="ai_image.png"):
    """Generates an image using OpenAI's DALL·E, downloads it, and returns the file path."""
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

        # Download and save the image
        response = requests.get(image_url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        print(f"Image saved to: {save_path}")

        # Display image in GUI
        display_image(save_path)

        return save_path  # Return the saved file path

    except Exception as e:
        error_message = f"Error generating or downloading image: {e}"
        print(error_message)

        # Update response field with error
        response_field.config(text=error_message, fg="red")

        return None


def display_image(image_path):
    """Displays the generated image in the GUI."""
    try:
        img = Image.open(image_path)
        img.thumbnail((300, 300))  # Resize for display
        img_tk = ImageTk.PhotoImage(img)

        # Update image label
        image_label.config(image=img_tk)
        image_label.image = img_tk  # Keep reference to avoid garbage collection

        # Hide error message if an image is successfully displayed
        response_field.config(text="Do you want to regenerate or proceed?", fg="white")

        # Show confirmation buttons
        regenerate_button.pack()
        proceed_button.pack()

        # Show download button
        download_button.pack()

    except Exception as e:
        print(f"Error displaying image: {e}")


def show_confirmation_buttons():
    """Displays the Regenerate and Proceed buttons after image generation."""
    regenerate_button.pack()
    proceed_button.pack()


def proceed_with_conversion():
    """Proceeds with converting the image into Minecraft blocks."""
    image_path = "ai_image.png"
    pixels = process_image(image_path)

    if pixels is not None:
        print(f"Image processed with shape: {pixels.shape}")

        # Convert pixels to Minecraft blocks
        block_grid = convert_pixels_to_blocks(pixels)

        # Generate and save .mcfunction file
        generate_mcfunction(block_grid)

        response_field.config(text="Minecraft function file generated! Run in-game with:\n/reload\n/function build_structure", fg="green")

    else:
        response_field.config(text="Image processing failed.", fg="red")


def process_image(image_path, size=(256, 256)):
    """Resizes and converts an image to an RGB pixel array."""
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize(size)
        return np.array(image)  # RGB Pixel Array

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def download_image():
    """Allows the user to download the image."""
    os.system(f"start {os.path.abspath('ai_image.png')}" if os.name == "nt" else f"open {os.path.abspath('ai_image.png')}")



















def euclidean_distance(color1, color2):
    """Computes the Euclidean distance between two RGB colors (avoiding overflow)."""
    return np.sqrt(sum((int(c1) - int(c2)) ** 2 for c1, c2 in zip(color1, color2)))


def closest_minecraft_block(rgb):
    """Finds the closest Minecraft block by calculating Euclidean distance."""

    # Define Minecraft block colors (RGB values)
    MINECRAFT_BLOCKS = {
        "white_wool": (255, 255, 255),
        "black_wool": (0, 0, 0),
        "red_wool": (255, 0, 0),
        "green_wool": (0, 255, 0),
        "blue_wool": (0, 0, 255),
        "yellow_wool": (255, 255, 0),
        "orange_wool": (255, 165, 0),
        "light_gray_wool": (200, 200, 200),
        "gray_wool": (100, 100, 100),
        "brown_wool": (139, 69, 19),
        "cyan_wool": (0, 255, 255),
        "purple_wool": (128, 0, 128),
        "sandstone": (237, 201, 175),
        "stone": (125, 125, 125),
        "grass_block": (127, 178, 56),
        "water": (64, 64, 255),
        "lava": (255, 69, 0),
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

    try:
        commands = []
        height = len(block_grid)

        # Iterate normally, but flip Y-coordinate placement
        for y, row in enumerate(block_grid):  # Y-axis (height)
            for x, block in enumerate(row):  # X-axis (width)
                commands.append(f"setblock ~3 ~{height - y} ~{x} minecraft:{block}")  # Flip Y positioning

        # Write to the .mcfunction file
        with open(MINECRAFT_FUNCTION_PATH, "w") as f:
            f.write("\n".join(commands))

        print(f".mcfunction file saved to: {MINECRAFT_FUNCTION_PATH}")

    except Exception as e:
        print(f"Error writing .mcfunction file: {e}")











def main():
    """Main function to generate, process, and convert the image into a Minecraft build."""
    setup_gui()




if __name__ == "__main__":
    main()
