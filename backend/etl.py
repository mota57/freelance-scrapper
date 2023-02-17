import models


def set_all_active():
    db = models.get_db()
    for r in db.get_all():
        r['is_active'] = True
        db.update_by_id(r['id'], {'is_active': True, 'name': r['name']})
        print("record " + str(r['id']) + "saved")


if __name__ == '__main__':
    set_all_active()
