import io
import sys
from nowatermark.cli import main


def test_detect_clean_text_exits_zero(tmp_path, capsys):
    f = tmp_path / "clean.txt"
    f.write_text("hello world", encoding="utf-8")
    code = main(["detect", str(f)])
    assert code == 0


def test_detect_watermarked_text_exits_one(tmp_path, capsys):
    f = tmp_path / "dirty.txt"
    f.write_text("hello​world", encoding="utf-8")
    code = main(["detect", str(f)])
    out = capsys.readouterr().out
    assert code == 1
    assert "U+200B" in out


def test_clean_writes_output_file(tmp_path):
    src = tmp_path / "dirty.txt"
    dst = tmp_path / "out.txt"
    src.write_text("hello​world", encoding="utf-8")
    code = main(["clean", str(src), "-o", str(dst)])
    assert code == 0
    assert dst.read_text(encoding="utf-8") == "helloworld"


def test_clean_stdin_stdout(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("hello​world"))
    code = main(["clean", "-"])
    out = capsys.readouterr().out
    assert code == 0
    assert out == "helloworld"


def test_clean_report_flag_prints_summary(tmp_path, capsys):
    src = tmp_path / "dirty.txt"
    src.write_text("a​b​c", encoding="utf-8")
    main(["clean", str(src), "-o", str(tmp_path / "out.txt"), "--report"])
    err = capsys.readouterr().err
    assert "U+200B" in err
    assert "2" in err


def test_detect_flags_homoglyph_word_but_does_not_change_exit_code(tmp_path, capsys):
    f = tmp_path / "homoglyph.txt"
    # Cyrillic а (U+0430) instead of Latin a -- no invisible chars at all
    f.write_text("this аttack has no invisible chars", encoding="utf-8")
    code = main(["detect", str(f)])
    out = capsys.readouterr().out
    assert code == 0  # heuristic finding must not affect the deterministic exit code
    assert "homoglyph" in out
    assert "аttack" in out


def test_detect_missing_file_prints_clean_error_not_traceback(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    code = main(["detect", str(missing)])
    err = capsys.readouterr().err
    assert code == 2
    assert "no such file" in err
    assert "Traceback" not in err


def test_clean_invalid_utf8_prints_clean_error(tmp_path, capsys):
    f = tmp_path / "bad_encoding.txt"
    f.write_bytes(b"\xff\xfe not valid utf-8")
    code = main(["clean", str(f)])
    err = capsys.readouterr().err
    assert code == 2
    assert "not valid UTF-8" in err
    assert "Traceback" not in err


def test_detect_directory_instead_of_file_prints_clean_error(tmp_path, capsys):
    code = main(["detect", str(tmp_path)])
    err = capsys.readouterr().err
    assert code == 2
    assert "directory" in err
    assert "Traceback" not in err


def test_clean_output_in_nonexistent_directory_prints_clean_error(tmp_path, capsys):
    src = tmp_path / "in.txt"
    src.write_text("hello world", encoding="utf-8")
    bad_output = tmp_path / "does_not_exist" / "out.txt"
    code = main(["clean", str(src), "-o", str(bad_output)])
    err = capsys.readouterr().err
    assert code == 2
    assert "no such file" in err
    assert "Traceback" not in err
