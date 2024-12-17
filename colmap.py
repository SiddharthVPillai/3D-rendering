import os
import subprocess

def run_colmap_pipeline(colmap_workspace):
    """
    Run the full COLMAP pipeline in a user-defined workspace.

    Args:
        colmap_workspace (str): Path to the COLMAP workspace directory containing `images`.
    """
    # Validate workspace paths
    database_path = os.path.join(colmap_workspace, "database.db")
    images_path = os.path.join(colmap_workspace, "images")
    sparse_path = os.path.join(colmap_workspace, "sparse")

    if not os.path.isdir(images_path):
        raise ValueError(f"Images directory not found at: {images_path}")

    # Ensure necessary paths exist
    os.makedirs(sparse_path, exist_ok=True)

    # Start Xvfb as a background process
    print("Starting Xvfb...")
    xvfb_process = subprocess.Popen(["Xvfb", ":1", "-screen", "0", "1024x768x16"])
    print("Xvfb started with PID:", xvfb_process.pid)

    try:
        # Set the DISPLAY environment variable for offscreen rendering
        os.environ["DISPLAY"] = ":1"

        # Step 1: Feature extraction
        print("Running feature extraction...")
        subprocess.run([
            "colmap", "feature_extractor",
            "--database_path", database_path,
            "--image_path", images_path
        ], check=True)

        # Step 2: Exhaustive matching
        print("Running exhaustive matching...")
        subprocess.run([
            "colmap", "exhaustive_matcher",
            "--database_path", database_path
        ], check=True)

        # Step 3: Mapping
        print("Running mapper...")
        subprocess.run([
            "colmap", "mapper",
            "--database_path", database_path,
            "--image_path", images_path,
            "--output_path", sparse_path
        ], check=True)

        # Step 4: Model conversion to PLY format
        model_input_path = os.path.join(sparse_path, "0")
        ply_output_path = os.path.join(model_input_path, "point_cloud.ply")

        print("Converting model to PLY format...")
        subprocess.run([
            "colmap", "model_converter",
            "--input_path", model_input_path,
            "--output_path", ply_output_path,
            "--output_type", "PLY"
        ], check=True)

        print("COLMAP pipeline completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during COLMAP execution: {e}")
    finally:
        # Terminate Xvfb process
        xvfb_process.terminate()
        xvfb_process.wait()
        print("Xvfb terminated.")

if __name__ == "__main__":
    colmap_workspace = './workspace/'
    run_colmap_pipeline(colmap_workspace)
