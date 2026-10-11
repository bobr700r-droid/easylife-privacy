// Kreslí og.png (1200×630), apple-touch-icon.png (180) a favicon.png (64) pro web EasyForLife.
// Spuštění (dělá web.py, když obrázky chybí): swift site/art.swift <docs> <ikona.webp>…
import AppKit

let args = CommandLine.arguments
let out = URL(fileURLWithPath: args[1])
let icons = args.dropFirst(2).compactMap { NSImage(contentsOfFile: $0) }

func color(_ hex: UInt32, _ a: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: a)
}
let tiles: [UInt32] = [0x2563EB, 0xE8731C, 0x0F9A62, 0x8B46D9]

/// Logo: 2×2 dlaždice v barvách rodin (stejné jako favicon.svg, viewBox 32).
func drawLogo(in r: CGRect) {
    let s = r.width / 32
    let rects = [(2, 17), (17, 17), (2, 2), (17, 2)] // Core Graphics: počátek vlevo dole
    for (i, (x, y)) in rects.enumerated() {
        let rr = CGRect(x: r.minX + CGFloat(x) * s, y: r.minY + CGFloat(y) * s, width: 13 * s, height: 13 * s)
        let radius = (i == 3 ? 6.5 : 4) * s
        color(tiles[i]).setFill()
        NSBezierPath(roundedRect: rr, xRadius: radius, yRadius: radius).fill()
    }
}

func render(_ w: Int, _ h: Int, _ name: String, _ draw: (CGRect) -> Void) {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4,
                               hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    NSGraphicsContext.current?.imageInterpolation = .high
    draw(CGRect(x: 0, y: 0, width: w, height: h))
    NSGraphicsContext.restoreGraphicsState()
    try! rep.representation(using: .png, properties: [:])!.write(to: out.appendingPathComponent(name))
}

func text(_ s: String, size: CGFloat, weight: NSFont.Weight, color c: NSColor, at p: CGPoint, kern: CGFloat = 0) {
    NSAttributedString(string: s, attributes: [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: c, .kern: kern]).draw(at: p)
}

// OG obrázek
render(1200, 630, "og.png") { r in
    color(0xF7F6F2).setFill(); r.fill()
    // ikony appek v mřížce vpravo, mírně natočené
    let cols = 4, size: CGFloat = 132, gap: CGFloat = 26
    for (i, img) in icons.prefix(12).enumerated() {
        let col = i % cols, row = i / cols
        let x = 610 + CGFloat(col) * (size + gap), y = 630 - 70 - CGFloat(row + 1) * size - CGFloat(row) * gap + (col % 2 == 0 ? 14 : -14)
        let rect = CGRect(x: x, y: y, width: size, height: size)
        NSGraphicsContext.saveGraphicsState()
        let sh = NSShadow(); sh.shadowBlurRadius = 18; sh.shadowOffset = NSSize(width: 0, height: -6); sh.shadowColor = color(0x14141E, 0.18); sh.set()
        let clip = NSBezierPath(roundedRect: rect, xRadius: size * 0.23, yRadius: size * 0.23)
        color(0xFFFFFF).setFill(); clip.fill()
        NSGraphicsContext.restoreGraphicsState()
        NSGraphicsContext.saveGraphicsState()
        clip.addClip(); img.draw(in: rect)
        NSGraphicsContext.restoreGraphicsState()
    }
    drawLogo(in: CGRect(x: 72, y: 430, width: 96, height: 96))
    text("EasyForLife", size: 80, weight: .heavy, color: color(0x17191C), at: CGPoint(x: 66, y: 280), kern: -3)
    text("Appky, které ulehčují život.", size: 30, weight: .semibold, color: color(0x17191C), at: CGPoint(x: 72, y: 228))
    text("Apps that make life easier.", size: 26, weight: .regular, color: color(0x5F6670), at: CGPoint(x: 72, y: 188))
    text("easyforlife.cz · easyforlife.eu", size: 26, weight: .bold, color: color(0x2563EB), at: CGPoint(x: 72, y: 76))
}

// apple-touch-icon (iOS si roh zakulatí sám) a favicon.png
render(180, 180, "apple-touch-icon.png") { r in
    color(0xFFFFFF).setFill(); r.fill()
    drawLogo(in: r.insetBy(dx: 26, dy: 26))
}
render(64, 64, "favicon.png") { r in drawLogo(in: r) }
print("art ok")
