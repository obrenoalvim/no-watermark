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
