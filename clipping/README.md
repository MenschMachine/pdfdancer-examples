# Clipping Path Test PDFs

This directory contains comprehensive clipping path test PDFs designed to test PDF processing engines' handling of various clipping scenarios.

## Test Categories

### Basic Clipping Tests (BasicClippingPathTestGenerator)

The `BasicClippingPathTestGenerator` creates fundamental clipping test scenarios commonly used in PDF processing:

1. **basic-rectangular-clipping-test.pdf** - Simple rectangular clipping with overlapping content
2. **basic-circular-clipping-test.pdf** - Circular and elliptical clipping tests  
3. **basic-polygon-clipping-test.pdf** - Triangle, pentagon, and star-shaped clipping paths
4. **basic-text-clipping-test.pdf** - Text clipping with rectangular and circular bounds
5. **basic-image-clipping-test.pdf** - Simulated image content clipping scenarios
6. **basic-overlapping-content-test.pdf** - Multiple overlapping shapes with shared clipping areas
7. **basic-nested-clipping-test.pdf** - Two and three-level nested clipping scenarios
8. **basic-winding-rule-test.pdf** - Demonstrates non-zero vs even-odd winding rules
9. **basic-multiple-clips-test.pdf** - Sequential and intersecting clip operations

### Extreme Edge Case Tests (ClippingPathTestGenerator)

The `ClippingPathTestGenerator` creates extreme edge cases and stress tests:

- **Degenerate cases**: Zero-area, negative dimensions, single points
- **Extreme coordinates**: Very large/small values, precision limits
- **Complex scenarios**: Self-intersecting paths, rapid changes, nested complexity
- **Performance tests**: High-complexity stress scenarios

## Usage

To generate all basic clipping test PDFs:

```bash
java -cp build/libs/pdf-engine-1.0-SNAPSHOT-all.jar com.tfc.BasicClippingPathTestGenerator
```

To generate all extreme edge case test PDFs:

```bash
java -cp build/libs/pdf-engine-1.0-SNAPSHOT-all.jar com.tfc.ClippingPathTestGenerator
```

Or run the individual test methods programmatically for specific test scenarios.

## Testing Notes

The basic clipping tests focus on common, real-world scenarios that PDF engines should handle correctly. They provide good coverage of typical clipping operations without being overly complex.

The extreme edge case tests push the boundaries of what's possible with clipping paths and help identify robustness issues in PDF processing engines.

All test files are designed to be:
- Small and efficient (typically under 2KB each)
- Self-contained with no external dependencies
- Clearly labeled and documented
- Suitable for automated testing and validation 