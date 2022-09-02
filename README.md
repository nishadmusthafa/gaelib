# GAELIB

This is a library that will help you start a web server on [Google App Engine](https://cloud.google.com/appengine/docs)

<!-- ## Description

An in-depth paragraph about your project and overview of use. -->

## Getting Started

### Dependencies

* Docker - to set up the environment for running tests.

### Using gaelib in your projects
To be documented

### Running tests

In your terminal make your way to the repo root
Build the container using 
```
docker build -t gaelib . 
```
Launch the Google datastore emulator
```
docker run --name=gaelib_ds -p 10088:8888  google/cloud-sdk gcloud beta emulators datastore start --host-port 0.0.0.0:8888 --project emulator --store-on-disk --consistency=1
```
Launch the container to run tests
```
./run_test_container.sh
```
You will now be logged in to the container. To run the tests
```
cd gaelib/tests
pytest
```

## Contributors

Here is a list of contributors

1. [Manmeet Singh](https://github.com/danishdevil)
2. [Nishad Musthafa](https://github.com/nishadmusthafa)
3. [Shantanu Mallik](https://github.com/shantanumallik)

## Version History

* 0.1.0 - Initial Release

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE License - see the LICENSE.md file for details
