# AI Image to Minecraft Builder

This program uses OpenAI's API to generate an image based on a user prompt, then processes the image and builds it in Minecraft.
<br>

## Setup Instructions

### 1. Create a Virtual Environment
This project uses **Pipenv** to manage dependencies. To set up the virtual environment, run:

```sh
pipenv install
```

To activate the virtual environment, use:
```python
pipenv shell
```
<br>
<br>


### 2. Create a .env File
Inside the project directory, create a file named .env. This file will store environment variables.

<br>
<br>


### 3. Add Variables to .env File
Open .env and add the following variables:
```python
KEY=your_openai_api_key_here
MINECRAFT_WORLD_PATH=C:\path\to\your\minecraft\world
MINECRAFT_LAUNCHER_PATH=C:\path\to\minecraft\launcher.exe
```
<br>
<br>


### 4. Install Missing Libraries/Packages
If you haven't installed dependencies yet, run:
```python
pipenv install
```
This will install all required packages automatically.

<br>


###### Note: If you're using a different method to manage dependencies, you may need to manually install required packages.
<br>

#### This project was tested using Minecraft Java 1.21.4
<br>