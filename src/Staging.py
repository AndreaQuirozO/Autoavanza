import os
import uuid
import shutil

class Staging:
    """
    Class that handles the creation of a temporary staging directory for processing files.

    Attributes:
        uniquename (uuid.UUID): A unique identifier for each staging instance.
        staging_path (str): The full path to the staging directory.
    """

    def __init__(self, prefix):
        """
        Initializes the Staging object with a unique directory under a temp folder.

        Args:
            prefix (str): Subfolder name under the 'temp' directory, typically describing the job type.
        """

        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.staging_path = os.path.join(root_dir, "temp", prefix)

    def run(self):
        """
        Clears any existing folder at the staging path and creates a new empty one.

        Returns:
            str: The path to the newly created staging directory.
        """
        self.free()
        os.makedirs(self.staging_path, exist_ok=True)
        return self.staging_path

    def free(self):
        """
        Deletes the staging directory if it exists.
        """
        if os.path.exists(self.staging_path):
            shutil.rmtree(self.staging_path)
