import os, sys, asyncio, dotenv

dotenv.load_dotenv()

# Set before anything Camoufox-related
os.environ["CAMOUFOX_PATH"] = "/mnt/data/camoufox"
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "")

# Windows compatibility (optional)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from camoufox import AsyncCamoufox

def startCamoufox():
    launch_args = {}
    
    # Render (Linux) Configuration
    if not sys.platform.startswith("win"):
        # This Linux path is where the browser is INSTALLED on the Render disk.
        CAMOUFOX_EXECUTABLE_PATH = (
            os.environ["CAMOUFOX_PATH"] + 
            "/camoufox-142.0.1-fork.26-lin.x86_64/firefox"
        )
        # Add the explicit path only for Linux/Render deployment
        launch_args["executable_path"] = CAMOUFOX_EXECUTABLE_PATH
    user_data_rel_path = 'context'

    if os.path.exists(user_data_rel_path):
        try:
            os.makedirs(user_data_rel_path, exist_ok=True)
            print(f"Created persistent browser context directory: {user_data_rel_path}")
        except OSError as e:
            # Handle potential permission errors during creation
            print(f"Error creating directory {user_data_rel_path}: {e}", file=sys.stderr)
    return AsyncCamoufox(
        # Don't delete data between runs
        persistent_context=True,
        # Stores user data in local folder
        user_data_dir='context',
        **launch_args,
        # Randomizes mouse cursor movements
        humanize=True,
        # Opens window for control
        headless=True,
        # Allow browser to store data in cache to make look less automated
        enable_cache=True,
        # Contrain the screen so I can see buttons and inputs, doesn't really work anyways

        # window=(1920, 1080),
        # Keep device and user agent settings the same so linkedin doesnt log me out
        os="windows",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",

    )

        

