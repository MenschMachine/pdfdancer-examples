# Text Fragment Test PDFs

This directory contains test PDF files used for testing text fragment finding and manipulation features.

## Generating Test PDFs

To generate all test PDFs in this directory, run:

```bash
./gradlew :compileTestJava
java -cp "$(./gradlew :printTestClasspath -q)" com.tfc.shootingstar.core.text.fragment.TextFragmentTestPDFGenerator
```

Or use the convenience script:

```bash
./generate-test-pdfs.sh
```

## Test PDFs

The generator creates the following test PDFs:

### Basic Tests
1. **simple-single-line.pdf** - Simple single-line text: "Hello world today"
2. **multi-element.pdf** - Text split across multiple elements (multiple showText operations)
3. **extra-whitespace.pdf** - Text with multiple spaces: "Hello    world     today"
4. **multi-line-paragraph.pdf** - Multi-line paragraph for testing line-based searches
5. **repeated-words.pdf** - Text with repeated words for find-all testing
6. **partial-word-match.pdf** - Text for testing partial word matching scenarios
7. **case-variation.pdf** - Text with case variations: "HELLO World hello WORLD"
8. **fragment-spanning-elements.pdf** - Text deliberately split mid-word across elements
9. **mixed-font-sizes.pdf** - Same text in different font sizes for position testing

### Edge Case Tests
10. **overlapping-matches.pdf** - Pattern "AAABBBCCC" for testing overlapping matches
11. **empty-document.pdf** - Empty PDF with no text content
12. **multiple-paragraphs.pdf** - Multiple paragraphs separated by vertical spacing
13. **unicode-text.pdf** - Unicode and special characters (accents, symbols)
14. **long-single-line.pdf** - Very long single line with repeated patterns
15. **element-splitting.pdf** - Text "abcdefghijk" for testing mid-element fragment operations

## Usage in Tests

These PDFs are used by `TextFragmentE2ETest` to validate:
- Text fragment finding with fuzzy whitespace matching
- Case-sensitive and case-insensitive searches
- Finding all occurrences of repeated text
- Making fragments transparent (rendering mode 3)
- Replacing text fragments with font substitution
- Position calculation accuracy

## Generator Source

The generator is implemented in:
`src/test/java/com/tfc/shootingstar/core/text/fragment/TextFragmentTestPDFGenerator.java`
