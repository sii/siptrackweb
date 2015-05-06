from siptrackweb.views import helpers

def make_device_association_list(device):
    ret = []
    for assoc in device.listAssociations(include = ['device']):
        path = helpers.make_browsable_path(assoc,
                ['device category', 'device tree'],
                include_root = False)
        ent = {'obj': assoc, 'path': path, 'type': 'association'}
        ret.append(ent)
    for ref in device.listReferences(include = ['device']):
        path = helpers.make_browsable_path(ref,
                ['device category', 'device tree'],
                include_root = False)
        ent = {'obj': ref, 'path': path, 'type': 'reference'}
        ret.append(ent)
    ret.sort()
    return ret


