# bart-gtfs
API consumer for the bart real time GTFS

## instructions:
`docker build . -t bartapi`
### to show parsing
`docker run bartapi`
### to hang the container for debugging
```
docker run -d --env SLEEP=1 --name bartapi_debug bartapi
docker exec -it bartapi_debug bash
```


Install protobuf for ubuntu, then for python.  acquire the .proto file needed and run protoc on it to create <filename>_pb2.py
  This is your proto ingester.
