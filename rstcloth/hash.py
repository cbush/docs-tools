import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin/')))

from rstcloth import RstCloth
import utils

def main(fn):
    r = RstCloth()

    if os.path.exists(fn):
        with open(fn, 'r') as f:
            existing = f.read()
    else:
        existing = None

    commit = utils.get_commit()

    r.directive('|commit| replace', '``{0}``'.format(commit))

    if r.get_block('_all')[0] == existing[:-1]:
        print('[build]: no new commit(s), not updating {0} ({1})'.format(fn, commit))
    else:
        r.write(fn)
        print('[build]: regenerated {0} with new commit hash: {1}'.format(fn, commit))

if __name__ == '__main__':
    main(sys.argv[1])
