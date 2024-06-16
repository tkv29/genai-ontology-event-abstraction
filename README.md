# GenAI Ontology-based Event Abstraction (GOEA)

This is a prototype implementation of the GOEA Methodology proposed in a bachelor thesis. The GOEA methodology proposes an approach to extract, normalize, and abstract terms using ontologies and Large Language Models. While the methodology itself is applicable to various domains, this prototype specifically focuses on testing it in the context of medications.

![methodology](https://github.com/tkv29/genai-ontology-event-abstraction/assets/73845255/74daf6f9-6198-4f2c-8a08-be570615df7b)


## Requirements

To run GOEA successfully, it is essential to obtain an OpenAI API key with adequate credits. Without a valid API key and sufficient balance, the extraction process cannot be performed. The current prices for the API can be found at [OpenAI Pricing](https://openai.com/api/pricing/).

## Installation

### Installation through Docker

1. Download the content folder from the GitHub repository as it contains example event logs and ontologies used in the bachelor thesis.
2. Download the Docker release.
3. Load the Docker Image: Open a terminal or command prompt and navigate to the directory where you downloaded the Docker image file. Run the following command to load the image: `docker load -i goea.tar`
4. Run the Docker Container: After the image is successfully loaded, run the following command to start the GOEA container: `docker run -p 8000:8000 goea`. This command will start the container and map port 8000 from the container to port 8000 on your local machine. You may need to use `sudo` depending on your system setup.
5. Access GOEA: Open a web browser and navigate to http://localhost:8000/. This will bring you to the prototype application, where you can enter your OpenAI API Key and start abstracting event logs.
6. Follow the walkthrough.

### Installation through Git Clone

1. Clone the repository using `git clone`.
2. Install Python and pip, and then install all the requirements listed in the `requirements.txt` file using pip.
3. Start the server by running `python3 manage.py runserver`.
4. Follow the walkthrough.

## Walkthrough

1. Enter your OpenAI API Key. If you enter the wrong key, click on the Key Icon to retype your key.
![image](https://github.com/tkv29/genai-ontology-event-abstraction/assets/73845255/7ad3292a-56f4-4011-9011-bcea16677b59)
2. Upload an Event Log as an XES file and an Ontology as an RDF or OWL file (you can find sample files in content folder that was used in the thesis). Please tick the box if you are using a custom ontology or not.
![image](https://github.com/tkv29/genai-ontology-event-abstraction/assets/73845255/edb18628-a7c7-48c4-9ba9-30dfb47e02aa)
3. Here you can check your uploaded event log and ontology as a string representation but also as a graphical representation. Nodes are color-coded as follows:
   - **Orange Nodes:** These nodes represent the target abstraction levels to which the blue nodes will be mapped.
   - **Blue Nodes:** These nodes represent the specific terms that will be abstracted to the corresponding orange nodes.
   - **Grey Nodes:** These nodes are not considered in the abstraction process at the current target abstraction level and are therefore visually distinguished from the relevant nodes.
![Bildschirmfoto_16-6-2024_231029_127 0 0 1](https://github.com/tkv29/genai-ontology-event-abstraction/assets/73845255/62e2b5ec-06d1-4628-85b8-60f3e6a16e72)

   Please select a target abstraction level using the slider.
4. Start the abstraction process by clicking on "GO - Event Abstraction"
5. After the abstraction process you can download the Event Logs with the Extracted Medications, Normalized Medications and Abstracted Medications.
![Bildschirmfoto_16-6-2024_231219_127 0 0 1](https://github.com/tkv29/genai-ontology-event-abstraction/assets/73845255/d71661ba-ab8c-4576-a58e-f2a78dc8034d)
