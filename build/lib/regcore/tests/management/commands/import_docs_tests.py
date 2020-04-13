from mock import Mock

from regcore.management.commands import import_docs


def test_scoped_files(tmpdir):
    """We get the file path components for all created files, regardless of
    how deep in the directory structure"""
    a = tmpdir.mkdir('a')
    b = tmpdir.mkdir('b')
    a.mkdir('1')
    a.mkdir('2')
    b.mkdir('1').mkdir('i')

    tmpdir.ensure('a', '1', 'i')
    tmpdir.ensure('a', '1', 'ii')
    tmpdir.ensure('a', '2', 'i')
    tmpdir.ensure('b', '1', 'i', 'A')
    tmpdir.ensure('b', '1', 'i', 'B')
    tmpdir.ensure('b', '1', 'i', 'C')

    result = {tuple(file_parts)
              for file_parts in import_docs.scoped_files(str(tmpdir))}
    # These should always begin with an empty string due to leaving in the
    # trailing slash
    assert result == {
        ('', 'a', '1', 'i'), ('', 'a', '1', 'ii'),
        ('', 'a', '2', 'i'),
        ('', 'b', '1', 'i', 'A'), ('', 'b', '1', 'i', 'B'),
        ('', 'b', '1', 'i', 'C'),
    }


def test_save_file(monkeypatch, tmpdir):
    """Saving a file should send it to a corresponding url"""
    monkeypatch.setattr(import_docs, 'Client', Mock())
    monkeypatch.setattr(import_docs, 'logger', Mock())
    # Client().put
    put = import_docs.Client.return_value.put
    put.return_value.status_code = 204

    tmpdir.mkdir('a').mkdir('1').join('i').write(b'content')
    import_docs.save_file(str(tmpdir), ['', 'a', '1', 'i'])
    assert put.call_args == (
        ('/a/1/i',), {'data': b'content', 'content_type': 'application/json'})
    assert import_docs.logger.info.called

    put.reset_mock()
    put.return_value.status_code = 404
    put.return_value.content = 'a'*1000
    import_docs.save_file(str(tmpdir), ['', 'a', '1', 'i'])
    assert import_docs.logger.error.called
    assert import_docs.logger.error.call_args[0][3] == 'a'*100    # trimmed
