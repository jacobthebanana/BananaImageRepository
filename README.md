# Banana Image Repository
Minimalistic AI-powered image repository. A pre-trained ResNet-v2 model labels uploaded images automatically. Uploads are stored in an S3-compatible backend. Built with Django and Bootstrap. 

Technology highlights:
- Python3, Django, and PostgreSQL.
- Bootstrap framework.
- Tensorflow-Serving.
- S3-compatible storage backends (MinIO.)
- Docker and Docker-compose. Spin up the whole thing (batteries included) in a minute or two.

# Getting Started 
Tools that you'll need: 
- Docker.
- Docker-Compose.

Start by making a copy of this git repo:
```bash
git clone https://github.com/jacobthebanana/BananaImageRepository.git && cd BananaImageRepository
```

## Deployment
It takes just three steps to spin up Banana Image Repository on your local machine. Before proceeding, make sure that you are in the same folder as `docker-compose.yml`.

### Retrieve a pre-trained ResnetV2 model
On a Linux machine, run the following to download and extract a pre-trained ResnetV2 image classification model from Google. 
```bash
mkdir models

wget -O labels.txt \
  https://github.com/jacobthebanana/BananaImageRepository/releases/download/files/labels.txt
wget -O models/resnet_v2_fp32_savedmodel_NHWC_jpg.tar.gz \
  http://download.tensorflow.org/models/official/20181001_resnet/savedmodels/resnet_v2_fp32_savedmodel_NHWC_jpg.tar.gz

tar -C models/ -xzvf models/resnet_v2_fp32_savedmodel_NHWC_jpg.tar.gz
mv models/resnet_v2_fp32_savedmodel_NHWC_jpg models/resnet
```

The directory structure should resemble the following:
```
bananaImageRepository
+ bananaImageRepository
+ imageRepository
+ s3
- models 
  - resnet
    - 1538687457
      - variables
        - variables.index
        - variables.data-00000-of-00001
- docker-compose.yml
- .env
- labels.txt
- manage.py
```

### Create the dot-env file
Sensitive parameters (access tokens, etc.) are stored in a `.env` file. For security reasons, the env file isn't included in the git repository. However, with the help of the template `env.example`, you could create your own `.env` file in a minute or two.
```bash
cp .env.example .env
```

Adjust `.env` with your favorite editor. 

When the user requests an image from the image repository, `S3_PUBLIC_URL` is the S3 server that would be presented to the user's browser. By default, the docker-compose file is configured to export the S3 server at port `9000` of the Docker Engine server. If you are running Docker on your local machine, the default `.env` value `S3_PUBLIC_URL=http://localhost:9000` would be sufficient. 

Adjust the hostname part (e.g., `localhost`) of `S3_PUBLIC_URL` if: 
- you are running the Docker Engine on a remote server, or 
- you are using an external S3 service (e.g., Google Cloud Storage). 

Be reminded that `S3_PUBLIC_URL` should include the protocol (e.g., `http://`), the hostname (e.g., `localhost`), and the port number (e.g., `9000`.) It should **not** include a trailing slash. For example, `http://localhost:8000` is fine, but `http://localhost:8000/` isn't okay and would prevent images from loading properly. 


### Start the server
Spin up a batteries-included Banana Image Repository server with the following commands:
```bash
docker-compose build  # This could take a while.
docker-compose up -d

# Initialize the database
docker-compose exec web /bin/sh -c \
  "python3 manage.py makemigrations imageRepository \
  && python3 manage.py migrate"
```

Assuming that you are running Docker Engine on your local machine, the Banana Image Repository would now be running at `http://localhost:8000/`. You would need to re-run `docker-compose up -d` to apply changes to `.env`. 


Two more folders would be created in the current directory. That's where all the data related to the Banana Image Repository is stored. Adjust the `volumes` sections of `docker-compose.yml` to store the data elsewhere. 
- `database` for PostgreSQL.
- `minio` for storing files uploaded to the local S3 server.

Stop the server with the following command:
```bash
docker-compose down
```

### Reverse Proxy and SSL Gateway
There are two ports to reverse-proxy. The exact port numbers could be customized in the Docker-compose file.
- port `8000` for the Image Repository Django web app.
- port `9000` for the local S3 backend. (Skip this port if you are using an external S3 service. e.g., Google Cloud Storage.) 


## Development and Testing
Banana Image Repository is built with Django in Python. Most of the logics are in `imageRepository/views.py` and `imageRepository/models.py`. Most of the parameters and constants are loaded as environment variables. Refer to `bananaImageRepository/settings.py` for details.

Make sure that the `venv` Python package is installed. Create a Python virtual environment (`venv`) and install the packages:
```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

Update `requirements.txt` before testing and deploying in case you've added any package: 
```bash
pip3 freeze > requirements.txt
```

### Testing
Refer to `imageRepository/tests.py` for the source of the tests.

Navigate to the root folder of this repository. Make sure that you've created a `.env` file in the same folder as `docker-compose.yml`. (Simply copying `.env.example` would suffice; please refer to the "deployment" section for details on the `.env` file.) 

**Important**: make sure the `DEMO=1` line is commented out in the `.env` file. A Banana Image Repository server in Demo mode would not save anything to S3. The test `imageRepository.tests.S3IntegrationTestCase` is almost guarenteed to give an error if the server is in demo mode.

Run a batteries-included test with the following commands:
```bash 
docker-compose build  # Rebuild the Docker image (from cache) before testing
docker-compose up -d  # In case you've updated the .env file
docker-compose exec web \
  python3 manage.py test
```

## Features and TODOs
- [x] Automatic image labeling.
- [x] Minimalistic user interface based on Bootstrap.
- [x] Demo mode (labeling works, but stores no user upload.)
- [ ] AI-powered image search.
- [ ] Access control.
- [ ] Real frontend (e.g., ReactJS.)

### Prospect: AI-powered semantic-aware image search
Architecture: On image upload, classify the image with a pre-trained image captioning model. This would generate a hidden caption vector, which a decoder (a recurrent neural network) could unroll into a human-readable sentence (a "caption") describing the image. Store both this caption and the hidden caption vector.

When the user performs a search, the encoder (complement of the hidden caption vector encoder) would encode the user's query sentence into a hidden caption vector of the same size. The Image Repository server would compare this query vector against the caption vectors of all images in the repository (e.g., using vector dot product.) The top few matches (highest dot product) would be presented to the user.

This extension to the project would allow users to go beyond a simple filtering of labels. A natural query sentence (e.g., "flying a kite" as opposed to "kites on the shelf") captures the relation and state of the objects. Including this information in the search would allow the image repository to gain considerably more insights into the users' intentions. Naturally, that would make it easier for users to find what they want, and would translate to a significant improvement in user experience. I'm excited to see how Shopify's resources and talents could allow us to improve user experiences with the help of AI. 