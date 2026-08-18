import Foundation
import AVFoundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// usage:
//   swift vidtool.swift info <video>
//   swift vidtool.swift grab <video> <outdir> <t1> <t2> ...      (seconds, exact frame)
//   swift vidtool.swift burst <video> <outdir> <start> <count>   (consecutive frames from start)

let args = CommandLine.arguments
guard args.count >= 3 else { print("bad args"); exit(1) }
let mode = args[1]
let url = URL(fileURLWithPath: args[2])
let asset = AVURLAsset(url: url)

guard let track = asset.tracks(withMediaType: .video).first else {
    print("ERROR: no video track"); exit(1)
}
let fps = track.nominalFrameRate
let dur = CMTimeGetSeconds(asset.duration)
let size = track.naturalSize.applying(track.preferredTransform)
let w = abs(size.width), h = abs(size.height)

if mode == "info" {
    print("duration_sec   : \(String(format: "%.3f", dur))")
    print("nominal_fps    : \(fps)")
    print("min_frame_dur  : \(CMTimeGetSeconds(track.minFrameDuration))")
    print("resolution     : \(Int(w)) x \(Int(h))")
    print("total_frames   : ~\(Int(dur * Double(fps)))")
    print("codec          : \(track.formatDescriptions.count) fmt desc")
    print("bitrate_mbps   : \(String(format: "%.2f", track.estimatedDataRate / 1_000_000))")
    exit(0)
}

let outDir = URL(fileURLWithPath: args[3])
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = .zero   // exact frame, no snapping
gen.requestedTimeToleranceAfter  = .zero
// keep frames legible but bounded
gen.maximumSize = CGSize(width: 1280, height: 1280)

var times: [Double] = []
if mode == "grab" {
    for i in 4..<args.count { if let t = Double(args[i]) { times.append(t) } }
} else if mode == "burst" {
    guard args.count >= 6, let start = Double(args[4]), let n = Int(args[5]) else {
        print("burst needs <start> <count>"); exit(1)
    }
    let step = 1.0 / Double(fps)
    for i in 0..<n { times.append(start + Double(i) * step) }
} else { print("unknown mode"); exit(1) }

for t in times {
    let ct = CMTime(seconds: t, preferredTimescale: 600)
    do {
        var actual = CMTime.zero
        let cg = try gen.copyCGImage(at: ct, actualTime: &actual)
        let label = String(format: "t%08.3f", t).replacingOccurrences(of: ".", with: "_")
        let out = outDir.appendingPathComponent("\(label).png")
        guard let dest = CGImageDestinationCreateWithURL(out as CFURL, UTType.png.identifier as CFString, 1, nil) else { continue }
        CGImageDestinationAddImage(dest, cg, nil)
        CGImageDestinationFinalize(dest)
        print(String(format: "%.3f -> actual %.4f  %@", t, CMTimeGetSeconds(actual), out.lastPathComponent))
    } catch {
        print("FAIL at \(t): \(error.localizedDescription)")
    }
}
