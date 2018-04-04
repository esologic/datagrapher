import pickle
from os import listdir, remove
from os.path import isfile, join

from code.library_python.logger import logger

if __name__ == "__main__":

    path = "."

    all_files = [f for f in listdir(path) if isfile(join(path, f))]

    pickle_files = filter(lambda x: x.endswith(".p"), all_files)

    for pickle_path in pickle_files:

        logger.info("Loading: " + pickle_path + " for rendering.")

        rendered = False

        with open(pickle_path, "rb") as file:

            try:

                dg_pickle = pickle.load(file)

                try:

                    prefex = pickle_path.split(".")[0]

                    new_path = prefex + ".png"

                    logger.info("Rendering: " + pickle_path + " to: " + str(new_path))

                    dg_pickle.render_as_image(new_path)
                    file.flush()

                    rendered = True

                    logger.info("Render complete, " + pickle_path + " removed.")

                except IndexError:
                    logger.warn("File: " + str(pickle_path) + " is a bad path")

            except IOError as e:
                logger.warn("Pickle file: " + str(pickle_path) + " is already open " + str(e))

        if rendered:
            remove(pickle_path)