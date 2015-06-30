import os

FIXTURES_ROOT = {
    'compute': 'fixtures',
}

class FileFixtures(object):
    def __init__(self, fixtures_type, sub_dir=''):
        script_dir = os.path.abspath(os.path.split(__file__)[0])
        self.root = os.path.join(script_dir, FIXTURES_ROOT[fixtures_type],
                                 sub_dir)

    def load(self, file):
        path = os.path.join(self.root, file)
        if os.path.exists(path):
            kwargs = {}

            with open(path, 'r', **kwargs) as fh:
                content = fh.read()
            return unicode(content)
        else:
            raise IOError(path)

class ComputeFileFixtures(FileFixtures):
    def __init__(self, sub_dir=''):
        super(ComputeFileFixtures, self).__init__(fixtures_type='compute',
                                                  sub_dir=sub_dir)

