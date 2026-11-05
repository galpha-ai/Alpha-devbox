"""Minimal, robust Markdown -> PDF via reportlab (headings, paragraphs, bullets, tables, code)."""
import re, sys, html
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table,
                                TableStyle, PageBreak)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# DejaVu covers Greek, subscripts, math symbols used in the document
import glob
font_paths = glob.glob('/usr/share/fonts/**/DejaVuSans.ttf', recursive=True)
mono_paths = glob.glob('/usr/share/fonts/**/DejaVuSansMono.ttf', recursive=True)
bold_paths = glob.glob('/usr/share/fonts/**/DejaVuSans-Bold.ttf', recursive=True)
if font_paths:
    pdfmetrics.registerFont(TTFont('DV', font_paths[0]))
    pdfmetrics.registerFont(TTFont('DVB', (bold_paths or font_paths)[0]))
    pdfmetrics.registerFont(TTFont('DVM', (mono_paths or font_paths)[0]))
    BASE, BOLD, MONO = 'DV', 'DVB', 'DVM'
else:
    BASE, BOLD, MONO = 'Helvetica', 'Helvetica-Bold', 'Courier'

ss = getSampleStyleSheet()
body = ParagraphStyle('body', parent=ss['Normal'], fontName=BASE, fontSize=9.2, leading=12.5,
                      spaceAfter=5)
h = {1: ParagraphStyle('h1', parent=body, fontName=BOLD, fontSize=17, leading=21, spaceBefore=14, spaceAfter=8),
     2: ParagraphStyle('h2', parent=body, fontName=BOLD, fontSize=13.5, leading=17, spaceBefore=12, spaceAfter=6),
     3: ParagraphStyle('h3', parent=body, fontName=BOLD, fontSize=11, leading=14, spaceBefore=9, spaceAfter=4)}
bullet = ParagraphStyle('bul', parent=body, leftIndent=14, bulletIndent=4)
quote = ParagraphStyle('q', parent=body, leftIndent=16, textColor=colors.HexColor('#333366'))
code = ParagraphStyle('code', parent=body, fontName=MONO, fontSize=7.4, leading=9.2,
                      backColor=colors.HexColor('#f4f4f4'), leftIndent=6, spaceAfter=6)
cell = ParagraphStyle('cell', parent=body, fontSize=7.6, leading=9.6, spaceAfter=0)

def inline(s):
    s = html.escape(s, quote=False)
    codes = []
    def stash(m):
        codes.append(m.group(1)); return '\x00%d\x00' % (len(codes)-1)
    s = re.sub(r'`([^`]+)`', stash, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: '<font face="%s">%s</font>' % (MONO, codes[int(m.group(1))]), s)
    return s

def build(md_path, pdf_path, title):
    lines = open(md_path, encoding='utf-8').read().split('\n')
    story, i = [], 0
    para = []
    def flush():
        nonlocal para
        if para:
            story.append(Paragraph(inline(' '.join(para)), body)); para = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            flush(); j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith('```'):
                buf.append(lines[j]); j += 1
            story.append(Preformatted('\n'.join(buf), code)); i = j + 1; continue
        if ln.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i+1]):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[\s:|-]+\|$', lines[i]):
                    cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                    rows.append([Paragraph(inline(c), cell) for c in cells])
                i += 1
            if rows:
                ncol = max(len(r) for r in rows)
                rows = [r + [Paragraph('', cell)] * (ncol - len(r)) for r in rows]
                w = (A4[0] - 3*cm) / ncol
                t = Table(rows, colWidths=[w]*ncol, repeatRows=1)
                t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.3, colors.grey),
                                       ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8e8f0')),
                                       ('VALIGN', (0,0), (-1,-1), 'TOP')]))
                story.append(t); story.append(Spacer(1, 6))
            continue
        m = re.match(r'^(#{1,3})\s+(.*)', ln)
        if m:
            flush(); lvl = len(m.group(1))
            story.append(Paragraph(inline(m.group(2)), h[lvl])); i += 1; continue
        if ln.strip() == '---':
            flush(); story.append(Spacer(1, 8)); i += 1; continue
        if re.match(r'^\s*[-*]\s+', ln):
            flush(); story.append(Paragraph(inline(re.sub(r'^\s*[-*]\s+', '', ln)), bullet, bulletText='•')); i += 1; continue
        if re.match(r'^\s*\d+\.\s+', ln):
            flush(); num = re.match(r'^\s*(\d+)\.', ln).group(1)
            story.append(Paragraph(inline(re.sub(r'^\s*\d+\.\s+', '', ln)), bullet, bulletText=num+'.')); i += 1; continue
        if ln.startswith('>'):
            flush(); buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i].lstrip('> ').rstrip()); i += 1
            story.append(Paragraph(inline(' '.join(buf)), quote)); continue
        if ln.strip() == '':
            flush(); i += 1; continue
        para.append(ln.strip()); i += 1
    flush()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm, title=title)
    doc.build(story)

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'document')
    print('wrote', sys.argv[2])
