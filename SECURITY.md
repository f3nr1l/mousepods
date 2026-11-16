# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 1.3.x (Flatpak stable, `main`) | ✅ |
| 1.2.x | ⚠️ fixes go into 1.3, please update |
| 1.1.x and older | ❌ please update |

## Reporting a vulnerability

Please **don't open a public issue**. Use GitHub's private report instead:
**Security** tab of the repository → **Report a vulnerability**. You will get an answer within a
few days, and credit in the fix if you want it.

## What is in scope

MousePods runs on your computer and talks to your earbuds. The parts that matter for security:

- The local web server on `127.0.0.1:8737`. It only answers requests addressed to `127.0.0.1` or
  `localhost` (DNS-rebinding guard). Pages from other origins are refused, except the official
  website and the browser extension, which may only read the head pose and recenter.
- The virtual mouse and joystick through `/dev/uinput`.
- The Bluetooth connection to the earbuds (it only reads sensor streams; it never touches firmware).
- The head-tracking DLLs placed in Proton prefixes by the Games page (`native/`), and the registry
  values the game bridge writes into those prefixes (`user.reg`, TrackIR tables).
- The experimental Windows driver in `windows/aap-poc` (test-signed proof of concept, not shipped in
  any release): reports are welcome, fixes are best effort.
- The Flatpak repository and its signing key.

Out of scope: bugs in BlueZ, the kernel, Wine/Proton or the games themselves.
