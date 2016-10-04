from odo import odo, drop, discover, resource
import os
import glob

sqlite_base = os.path.join('sqlite:///', 'project', 'server', 'dev.sqlite')

for csv in glob.glob(os.path.join('fixtures', '*.csv')):

    table = os.path.splitext(os.path.split(csv)[-1])[0]

    con = '::'.join([sqlite_base, table])

    try:
        drop(con)
    except:
        pass

    csvfile = os.path.join('fixtures', '{}.csv'.format(table))
    dshape = discover(resource(csvfile))
    t = odo(csvfile, con, dshape=dshape)
