# pdfminify
[![Build Status](https://travis-ci.org/johndoe31415/pdfminify.svg?branch=master)](https://travis-ci.org/johndoe31415/pdfminify)


pdfminify is intended to re-compress PDF images while operating directly at PDF
level (i.e., no re-compression using PostScript). It parses the PDF file,
hashes all image references, re-links resources that are duplicate (i.e., have
the same MD5 hash value) and also is able to re-compress images which are
stored with lossless compression in order to use JPEG. It tries to calculate
the physical extent of the images (which, depending on the inclusion method,
can be a bit messy) and then is able to calculate the actual image resolution.
If it exceeds a given target resolution, it can also re-sample images (i.e.,
re-scaling them using ImageMagick) before re-integrating them into the target
PDF.

In particular, I wrote this software because PDFs generated by the libcairo PDF
export are *huge*. Images that are used are included a dozen times and only
lossless compression is used. Therefore I use pdfminify to decrease the
filesize later.

Another use for pdfminify is that it is able to convert PDFs into PDF/A-1b
compliant PDF files. Since this is something that's really difficult to do,
there are no guarantees regarding the resulting PDF -- please check for
yourself if the results still behave identical to your source version.

# Requirements
pdfminify needs at least Python 3.5. It furthermore uses the "identify" and
"convert" utilities of ImageMagick. It uses the former to determine the width,
height, colorspace and bits per component of image files and the latter to
convert images from PNM (the internal format that pdfminify is capable of
writing natively) to JPEG.

# Acknowledgments
pdfminify uses the Toy Parser Generator (TPG) of Christophe Delord
(http://cdsoft.fr/tpg/). It is included (tpg.py file) and licensed under the
GNU LGPL v2.1 or any later version. Despite its name, it is far from a toy. In
fact, it is the most beautiful parser generator I have ever worked with and
makes grammars and parsing exceptionally easy, even for people without any
previous parsing experience. If you need parsing and use Python, TPG is *the*
go-to solution I would recommend. Seriously, it's amazing. Check it out.

In order to be able to easily create PDF/A-1b files, pdfminify also includes
the ICC sRGB color profile "sRGB_IEC61966-2-1_black scaled.icc". It is
distributed under its own license which is included in the EXTERNAL_LICENSES.md
file.

When signing documents, a Type1 font is included in the resulting PDF in order
to display metadata about the generated signature. As a default font, one of
the Bitstream Charter fonts which was contributed to the X consortium
(Bitstream Charter Serif) is included with pdfminify. It also has its own
copyright and license notice in EXTERNAL_LICENSES.md.

# License
pdfminify is licensed under the GNU GPL v3 (except for external components as
TPG, which has its own license). Later versions of the GPL are explicitly
excluded.

TPG (Toy Parser Generator) and the ICC sRGB color profile fall under their
respective licenses.

# Usage
<pre>
$ ./pdfminify --help
usage: pdfminify [-h] [-d dpi] [-j] [--jpeg-quality percent]
                 [--no-downscaling] [--cropbox x,y,w,h]
                 [--unit {cm,inch,mm,native}] [--one-bit-alpha]
                 [--remove-alpha] [--background-color color]
                 [--strip-metadata] [--saveimgdir path] [--raw-output]
                 [--pretty-pdf] [--no-xref-stream] [--no-object-streams]
                 [--pdfa-1b] [--color-profile iccfile] [--sign-cert certfile]
                 [--sign-key keyfile] [--sign-chain pemfile] [--signer name]
                 [--sign-location hostname] [--sign-contact-info infotext]
                 [--sign-reason reason] [--sign-page pageno]
                 [--sign-font pfbfile] [--sign-pos x,y] [--embed-payload path]
                 [--no-pdf-tagging] [--decompress-data] [--analyze]
                 [--dump-xref-table] [--no-filters] [-v]
                 pdf_in pdf_out

positional arguments:
  pdf_in                Input PDF file.
  pdf_out               Output PDF file.

optional arguments:
  -h, --help            show this help message and exit
  -d dpi, --target-dpi dpi
                        Default resoulution to which images will be resampled
                        at. Defaults to 150 dots per inch (dpi).
  -j, --jpeg-images     Convert images to JPEG format. This means that lossy
                        compression is used that however often yields a much
                        higher compression ratio.
  --jpeg-quality percent
                        When converting images to JPEG format, the parameter
                        gives the compression quality. It is an integer from
                        0-100 (higher is better, but creates also larger
                        output files).
  --no-downscaling      Do not apply downscaling filter on the PDF, take all
                        images as they are.
  --cropbox x,y,w,h     Crop pages by additionally adding a /CropBox to all
                        pages of the PDF file. Pages will be cropped at offset
                        (x, y) to a width (w, h). Must be given in the format
                        x,y,w,h. The unit in which offset, width and height
                        are given can be specified using the --unit parameter.
  --unit {cm,inch,mm,native}
                        Specify the unit of measurement that is used for input
                        and output. Can be any of cm, inch, mm, native,
                        defaults to native. One native PDF unit equals 1/72th
                        of an inch.
  --one-bit-alpha       Force all alpha channels in images to use a color
                        depth of one bit. This will make transparent images
                        have rougher edges, but saves additional space.
  --remove-alpha        Entirely remove the alpha channel (i.e., transparency)
                        of all images. The color which with transparent areas
                        are replaced with can be specified using the
                        --background-color command line option.
  --background-color color
                        When removing alpha channels, specifies the color that
                        should be used as background. Defaults to white.
                        Hexadecimal values can be specified as well in the
                        format '#rrggbb'.
  --strip-metadata      Strip metadata inside PDF objects that is not strictly
                        required, such as /PTEX.* entries inside object
                        content.
  --saveimgdir path     When specified, save all handled images as individual
                        files into the specified directory. Useful for image
                        extraction from a PDF as well as debugging.
  --raw-output          When saving images externally, save them in exactly
                        the format in which they're also present inside the
                        PDF. Note that this will produce raw image files in
                        some cases which won't have any header (but just
                        contain pixel data). Less useful for image extraction,
                        but can make sense for debugging.
  --pretty-pdf          Write pretty PDF files, i.e., format all dictionaries
                        so they're well-readable regarding indentation.
                        Increases required file size a tiny bit and increases
                        generation time of the PDF a little, but produces
                        easily debuggable PDFs.
  --no-xref-stream      Do not write the XRef table as a XRef stream, but
                        instead write a classical PDF XRef table and trailer.
                        This will increase the file size a bit, but might
                        improve compatibility with old PDF readers (XRef
                        streams are supported only starting with PDF 1.5).
                        XRef-streams are a prerequisite to object stream
                        compression, so if XRef-streams are disabled, so will
                        also be object streams (e.g, --no-object-streams is
                        implied).
  --no-object-streams   Do not compress objects into object-streams. Object
                        stream compression is introduced with PDF 1.5 and
                        means that multiple simple objects (without any stream
                        data) are concatenated together and compressed
                        together into one large stream object.
  --pdfa-1b             Try to create a PDF/A-1b compliant PDF document.
                        Implies --no-xref-stream, --no-object-streams,
                        --remove-alpha, removes transpacency groups and adds a
                        PDF/A entry into XMP metadata.
  --color-profile iccfile
                        When creating a PDF/A-1b PDF, gives the Internal Color
                        Consortium (ICC) color profile that should be embedded
                        into the PDF as part of the output intent. When
                        omitted, it defaults to the sRGB IEC61966 v2 "black
                        scaled" profile which is included within pdfminify.
  --sign-cert certfile  pdfminify can additionally cryptographically sign your
                        result PDF file with an X.509 certificate and
                        corresponding key. This parameter specifies the
                        certificate filename.
  --sign-key keyfile    This parameter specifies the key filename, also in PEM
                        format.
  --sign-chain pemfile  When signing a PDF, this gives the PEM-formatted
                        certificate chain file. Can be omitted if this should
                        not be included in the PKCS#7 signature.
  --signer name         The name of the person signing the document.
  --sign-location hostname
                        The location of the signing, usually a hostname.
  --sign-contact-info infotext
                        A contact information field under which the signer can
                        be reached. Usually a phone number of email address.
  --sign-reason reason  The reason why the document was signed.
  --sign-page pageno    Page number on which the signature should be
                        displayed. Defaults to 1.
  --sign-font pfbfile   To be able to include text in the signature, a T1 font
                        must be included into the PDF. This gives the filename
                        of the font that is to be used for that purpose. Must
                        be in PFB (PostScript Font Binary) file format and
                        will be included in the result PDF in full. Defaults
                        to the Bitstream Charter Serif font that is included
                        within pdfminify.
  --sign-pos x,y        Determines where the signature will be placed on the
                        page. Units are determined by the --unit variable and
                        position is relative to lower left corner.
  --embed-payload path  Embed an opaque file as a payload into the PDF as a
                        valid PDF object. This is useful only if you want to
                        place an easter egg inside your PDF file.
  --no-pdf-tagging      Omit tagging the PDF file with a reference to
                        pdfminify and the used version.
  --decompress-data     Decompress all FlateDecode compressed data in the
                        file. Useful only for debugging.
  --analyze             Perform an analysis of the read PDF file and dump out
                        useful information about it.
  --dump-xref-table     Dump out the XRef table that was read from the input
                        PDF file. Mainly useful for debugging.
  --no-filters          Do not apply any filters on the source PDF whatsoever,
                        just read it in and write it back out. This is useful
                        to reformat a PDF and/or debug the PDF reader/writer
                        facilities without introducing other sources of
                        malformed PDF generation.
  -v, --verbose         Show verbose messages during conversation. Can be
                        specified multiple times to increase log level.
</pre>

# PDF reading/writing
pdfminify uses its own PDF parser because for this particular purpose, neither
PyPDF2 nor pdfrw (which I both tried to use) seem suitable. This PDF
reader/writer is therefore is implemented in its own (included) library in the
"llpdf" subdirectory. It's the "low-level PDF" library because in contrast to
other PDF libraries, it has very little abstraction of the PDF file itself (and
exposes all the ugly PDF internals to the poor user). Feel free to play around
with it as you like!

# Bugs
PDF is an inherently messy format and parsing it really isn't pretty. I've
implemented only what I needed to implement in order to get my job done. I'm
sure there's dozens of examples in which pdfminify just plainly doesn't work or
creates broken output PDFs. Please feel free to fix these errors and send in a
pull request. I think it's a genuinely useful tool and therefore would be nice
to support a wider variety of PDFs than just those that I happen to generate.

If you encounter an issue but are unable to fix it because you don't know
enough about Python, PDF (or either), I will still look at your issue if you
report it on GitHub. However due to my lack of time, I cannot promise that I
can fix it -- to be honest, PDF is so complicated that I'm not even sure that I
can find what the issue is. In any case, be sure to include a minimal example
PDF that demonstrates the issue in the bug report.

