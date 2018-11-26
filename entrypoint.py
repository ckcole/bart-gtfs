import datetime, time, os, requests
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.json_format import MessageToDict

import psycopg2
from psycopg2.extras import execute_values

import gtfs_realtime_pb2


#########################
# TODO:  /opt/entrypoint.py:25: RuntimeWarning: Unexpected end-group tag: Not all data was converted
# msg.ParseFromString(data[pos:pos + next_pos])
#
#  THis should be fine,  it looks like we're still getting all the data
#  It looks like a failure to parse the header,  which isn't important.
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


def flatten_gtfs_rt_dict(parsed_entities, scrape_time):
    '''
    Given a list of trip dictionaries,  flatten that dictionary into a list of Stops per trip
    returns rows that can be put into a SQL db
    '''
    output_list = []
    for entity in parsed_entities:
        _id = entity['id']
        tripId = entity['tripUpdate']['trip']['tripId']
        for stop in entity['tripUpdate']['stopTimeUpdate']:
            row = {'id': _id, 'scrape_time': scrape_time}
            row['trip_id'] = tripId
            row['stop_id'] = stop['stopId']
            row['stop_sequence'] = int(stop['stopSequence'])
            for event in ('arrival', 'departure'):
                row[event + '_delay'] = int(stop[event]['delay'])
                row[event + '_time'] = datetime.datetime.fromtimestamp(int(stop[event]['time']))
                row[event + '_uncertainty'] = int(stop[event]['uncertainty'])
            output_list.append(row)
    return output_list


def upload_to_db(data):
    conn = psycopg2.connect('host=docker.for.mac.localhost dbname=test user=Cameron')
    cur = conn.cursor()
    target = (
        'arrival_delay', 'arrival_time', 'arrival_uncertainty', 'departure_delay',
        'departure_time', 'departure_uncertainty', 'stop_id', 'stop_sequence', 'trip_id',
        'scrape_time'
    )
    insert_str = 'INSERT INTO gtfs_rt (' + ', '.join(target) + ') VALUES %s'
    psql_out = []
    for row in data:
        psql_out.append(tuple([row[t] for t in target]))
    print 'Uploading {} rows'.format(len(psql_out))
    execute_values(cur, insert_str, psql_out)
    conn.commit()


if __name__ == '__main__' and not os.environ.get('SLEEP', False):
    # Google GTFS-rt proto: https://developers.google.com/transit/gtfs-realtime/gtfs-realtime-proto
    gtfsrt_response = requests.get('http://api.bart.gov/gtfsrt/tripupdate.aspx')
    scrape_time = datetime.datetime.now()
    parsed_entities = parse_gtfs_rt(gtfsrt_response.content)
    output = flatten_gtfs_rt_dict(parsed_entities, scrape_time)
    print 'Rows in output array: {}'.format(len(output))
    upload_to_db(output)

if os.environ.get('SLEEP', False):
    while True:
        print "jsut sleepin"
        time.sleep(60)
