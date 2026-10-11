// Ikona FotoDesku – styl EasyForLife (jako Salónky, Navigace): přechod, jeden bílý symbol, jemné kružnice, dlouhý stín.
// Tmavé „studiové“ pozadí a zlatý objektiv odliší FotoDesk od modrého CRMDesku i od FotoPlánu a FotoTipu.
// Spuštění: swift site/fotodesk-icon.swift <výstup.png> [light|dark|tinted]
import AppKit

let mode = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "light"
func c(_ hex: UInt32, _ a: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: a)
}
func rr(_ x: Double, _ y: Double, _ w: Double, _ h: Double, _ r: Double) -> NSBezierPath {
    NSBezierPath(roundedRect: NSRect(x: x, y: y, width: w, height: h), xRadius: r, yRadius: r)
}
func circle(_ x: Double, _ y: Double, _ r: Double) -> NSBezierPath {
    NSBezierPath(ovalIn: NSRect(x: x - r, y: y - r, width: 2 * r, height: 2 * r))
}

// Fotoaparát (počátek vlevo dole)
let body = rr(196, 286, 632, 420, 104)
let hump = rr(372, 640, 280, 132, 44)
let lensC = (512.0, 492.0)
let gold = mode == "tinted" ? (0xD8D8D8 as UInt32, 0xB8B8B8 as UInt32) : (0xFFD66B as UInt32, 0xE8A317 as UInt32)

let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: 1024, pixelsHigh: 1024, bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let ctx = NSGraphicsContext.current!.cgContext
let full = NSRect(x: 0, y: 0, width: 1024, height: 1024)

// Pozadí
switch mode {
case "tinted": c(0x000000).setFill(); full.fill()
case "dark": NSGradient(colors: [c(0x23252F), c(0x14151B), c(0x0B0B0F)], atLocations: [0, 0.55, 1], colorSpace: .sRGB)!.draw(in: full, angle: -45)
default: NSGradient(colors: [c(0x454B66), c(0x262938), c(0x14151D)], atLocations: [0, 0.55, 1], colorSpace: .sRGB)!.draw(in: full, angle: -45)
}
if mode != "tinted" {
    for r in [260.0, 400.0, 540.0, 680.0] {
        c(0xFFFFFF, 0.06).setStroke()
        let ring = circle(512, 492, r); ring.lineWidth = 6; ring.stroke()
    }
    // Dlouhý stín dolů doprava
    ctx.saveGState(); ctx.setAlpha(0.35); ctx.beginTransparencyLayer(auxiliaryInfo: nil)
    c(0x05050A).setFill()
    for step in stride(from: 0.0, through: 420, by: 3) {
        ctx.saveGState(); ctx.translateBy(x: step, y: -step); body.fill(); hump.fill(); ctx.restoreGState()
    }
    ctx.endTransparencyLayer(); ctx.restoreGState()
}

// Tělo – bílé s jemným stínováním
func fill(_ p: NSBezierPath, _ top: UInt32, _ bottom: UInt32) { NSGradient(starting: c(top), ending: c(bottom))!.draw(in: p, angle: -90) }
fill(hump, 0xFFFFFF, 0xEDEDF2)
fill(body, 0xFFFFFF, 0xE6E6EC)
// Objektiv: tmavý otvor, zlatý prstenec, sklo s odleskem
let bgLens: UInt32 = mode == "tinted" ? 0x000000 : 0x1B1D27
c(bgLens).setFill(); circle(lensC.0, lensC.1, 168).fill()
NSGradient(starting: c(gold.0), ending: c(gold.1))!.draw(in: circle(lensC.0, lensC.1, 138), angle: -60)
c(bgLens).setFill(); circle(lensC.0, lensC.1, 104).fill()
NSGradient(starting: c(mode == "tinted" ? 0x333333 : 0x3B4260), ending: c(mode == "tinted" ? 0x111111 : 0x161822))!.draw(in: circle(lensC.0, lensC.1, 84), angle: -60)
c(0xFFFFFF, 0.85).setFill(); circle(lensC.0 - 34, lensC.1 + 36, 22).fill()
c(0xFFFFFF, 0.45).setFill(); circle(lensC.0 + 30, lensC.1 - 28, 10).fill()
// Blesk a spoušť
NSGradient(starting: c(gold.0), ending: c(gold.1))!.draw(in: rr(668, 602, 96, 52, 22), angle: -90)
c(0xD9D9E0).setFill(); rr(250, 708, 92, 36, 16).fill()

NSGraphicsContext.current = nil
let flat = CGContext(data: nil, width: 1024, height: 1024, bitsPerComponent: 8, bytesPerRow: 0,
                     space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
flat.draw(rep.cgImage!, in: CGRect(x: 0, y: 0, width: 1024, height: 1024))
try! NSBitmapImageRep(cgImage: flat.makeImage()!).representation(using: .png, properties: [:])!
    .write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
