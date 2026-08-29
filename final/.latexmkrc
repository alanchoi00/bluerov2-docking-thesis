# Build with: latexmk
# Runs pdflatex + bibtex until stable, and teaches latexmk the nomencl step
# (makeindex on main.nlo -> main.nls) so the list of symbols builds in one pass.
$pdf_mode = 1;
add_cus_dep('nlo', 'nls', 0, 'makenlo2nls');
sub makenlo2nls {
    system("makeindex -s nomencl.ist -o \"$_[0].nls\" \"$_[0].nlo\"");
}
push @generated_exts, 'nlo', 'nls';
