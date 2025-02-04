import os
import logging
import yaml
import importlib
import pandas as pd
from .module import Module

BASE_DIR = "/path/to/base"
SPECTRA_DIR = os.path.join(BASE_DIR, "spectra")

class Classifier(Module):
    def __init__(self, code_config, config):
        super().__init__(config)
        self.code = code_config.get("code")
        self.config_file = code_config.get("config_file")
        self.handler = self.load_handler(self.code)

    def load_handler(self, code):
        # Dynamically load the handler for the specified classification code
        module = importlib.import_module(f"tides_pipe.classification_handlers.{code}")
        return module.ClassificationHandler(self.config_file)

    def classify(self, spectrum_path):
        if not os.path.exists(spectrum_path):
            self.logger.error(f"Spectrum file {spectrum_path} not found.")
            return None

        self.logger.info(f"Classifying spectrum: {spectrum_path} using {self.code}")
        result = self.handler.classify(spectrum_path)
        self.logger.info(f"Classification complete for: {spectrum_path} using {self.code}")
        return result

def run(night=None, objects=None, logger=None, config=None):
    with open(os.path.join(config['base_dir'], "config/config.yml"), 'r') as f:
        config = yaml.safe_load(f).get("classification", {})

    codes = config.get("codes", [])
    classifiers = [Classifier(code_config, config) for code_config in codes]

    for classifier in classifiers:
        classifier.set_logger(logger)

    results = []
    if night:
        spectra_night_dir = os.path.join(config['spectra_dir'], night)
        if not os.path.exists(spectra_night_dir):
            logger.error(f"No spectra found for night {night}.")
            return

        if objects:
            for obj in objects:
                spectrum_path = os.path.join(spectra_night_dir, obj)
                result = {"obj_name": obj}
                for classifier in classifiers:
                    classification_result = classifier.classify(spectrum_path)
                    if classification_result:
                        result.update({
                            f"auto_class_{classifier.code}": classification_result.get("result"),
                            f"auto_class_subclass_{classifier.code}": classification_result.get("subclass"),
                            f"auto_class_prob_{classifier.code}": classification_result.get("probability")
                        })
                results.append(result)
        else:
            for spectrum_file in os.listdir(spectra_night_dir):
                if spectrum_file.endswith(".txt"):
                    spectrum_path = os.path.join(spectra_night_dir, spectrum_file)
                    result = {"obj_name": spectrum_file}
                    for classifier in classifiers:
                        classification_result = classifier.classify(spectrum_path)
                        if classification_result:
                            result.update({
                                f"auto_class_{classifier.code}": classification_result.get("result"),
                                f"auto_class_subclass_{classifier.code}": classification_result.get("subclass"),
                                f"auto_class_prob_{classifier.code}": classification_result.get("probability")
                            })
                    results.append(result)
    else:
        logger.error("No night specified for classification.")
        return None

    # Aggregate results
    for result in results:
        for classifier in classifiers:
            if f"auto_class_{classifier.code}" in result:
                result["auto_class_agg"] = result[f"auto_class_{classifier.code}"]
                result["auto_class_subclass_agg"] = result[f"auto_class_subclass_{classifier.code}"]
                result["auto_class_prob_agg"] = result[f"auto_class_prob_{classifier.code}"]
                break

    results_df = pd.DataFrame(results)
    results_file = os.path.join(config['spectra_dir'], f"{night}_classification_results.csv")
    results_df.to_csv(results_file, index=False)
    logger.info(f"Classification results saved to {results_file}")
    return results_file