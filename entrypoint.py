import time, os
import requests
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.json_format import MessageToDict

import gtfs_realtime_pb2


#########################
# TODO:  /opt/entrypoint.py:25: RuntimeWarning: Unexpected end-group tag: Not all data was converted
# msg.ParseFromString(data[pos:pos + next_pos])
#
#  THis should be fine,  it looks like we're still getting all the data
###########################

def parse_gtfs_rt(data):
    '''
    Return a parsed dictionary of the Bart GTFS realtime feed.
    Response is in some Varint32 encoding.
    Requires a .proto file to read from schema, uses protobuf to read.
    https://groups.google.com/forum/#!topic/bart-developers/w715p0WxSSs
    '''

    proto = gtfs_realtime_pb2
    decoder = _DecodeVarint32

    # buffer to read varint32
    # https://stackoverflow.com/questions/11484700/python-example-for-reading-multiple-protobuf-messages-from-a-stream
    next_pos, pos = 0, 0
    while pos < len(data):
        msg = proto.FeedMessage()
        next_pos, pos = decoder(data, pos)
        msg.ParseFromString(data[pos:pos + next_pos])
        pos += next_pos

    print "done!"
    return MessageToDict(msg)['entity']


def flatten_gtfs_rt_dict(parsed_entities):
    '''
    Given a list of trip dictionaries,  flatten that dictionary into a list of Stops per trip
    returns rows that can be put into a SQL db
    '''
    output_list = []
    for entity in parsed_entities:
        _id = entity['id']
        tripId = entity['tripUpdate']['trip']['tripId']
        for stop in entity['tripUpdate']['stopTimeUpdate']:
            row = {'id': _id}
            row['tripId'] = tripId
            row['stopId'] = stop['stopId']
            row['stopSequence'] = stop['stopSequence']
            for event in ('arrival', 'departure'):
                row[event + 'Delay'] = stop[event]['delay']
                row[event + 'Time'] = stop[event]['time']
                row[event + 'Uncertainty'] = stop[event]['uncertainty']
            output_list.append(row)
    return output_list


if __name__ == '__main__' and not os.environ.get('SLEEP', False):
    # Google GTFS-rt proto: https://developers.google.com/transit/gtfs-realtime/gtfs-realtime-proto
    gtfsrt_response = requests.get('http://api.bart.gov/gtfsrt/tripupdate.aspx')
    parsed_entities = parse_gtfs_rt(gtfsrt_response.content)
    output = flatten_gtfs_rt_dict(parsed_entities)
    for x in parsed_entities:
        print x['id'], len(x['tripUpdate']['stopTimeUpdate'])
    print 'Rows in output array: {}'.format(len(output))

if os.environ.get('SLEEP', False):
    while True:
        print "jsut sleepin"
        time.sleep(60)
