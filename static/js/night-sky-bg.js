/**
 * night-sky-bg.js - Nền bầu trời đêm đầy sao, dải Ngân Hà & vệt sao băng nhẹ nhàng (Astrophotography Style)
 * Chỉ kích hoạt ở chế độ Tối (data-theme="dark") cho các trang sau đăng nhập.
 * Chu kỳ lặp sao nền 25 giây, 30fps mượt mà, camera cố định.
 */
(function () {
    "use strict";

    const canvas = document.getElementById("nightSkyBgCanvas");
    if (!canvas || !canvas.getContext) {
        window.NightSkyBg = { start() {}, stop() {} };
        return;
    }

    const ctx = canvas.getContext("2d", { alpha: false });
    const LOOP_SECONDS = 25;
    const TARGET_FPS = 30;
    const FRAME_INTERVAL = 1000 / TARGET_FPS;
    const TWO_PI = Math.PI * 2;
    const reducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let baseCanvas = null;
    let baseCtx = null;
    let width = 0;
    let height = 0;
    let dpr = 1;
    let twinklingStars = [];
    let shootingStars = [];
    let nextMeteorTime = 0;
    let running = false;
    let rafId = null;
    let startTime = 0;
    let lastDrawTime = 0;

    // Tạo sprite sao lấp lánh mềm sẵn để render hiệu năng cao ở 30fps
    function createStarSprite(size, coreColor, midColor, outerColor) {
        const off = document.createElement("canvas");
        off.width = size;
        off.height = size;
        const octx = off.getContext("2d");
        const c = size / 2;
        const g = octx.createRadialGradient(c, c, 0, c, c, c);
        g.addColorStop(0, coreColor);
        g.addColorStop(0.2, midColor);
        g.addColorStop(0.5, outerColor);
        g.addColorStop(1, "rgba(0, 0, 0, 0)");
        octx.fillStyle = g;
        octx.fillRect(0, 0, size, size);
        return off;
    }

    const whiteSprite = createStarSprite(
        32,
        "rgba(255, 255, 255, 1)",
        "rgba(238, 246, 255, 0.72)",
        "rgba(185, 220, 255, 0.14)"
    );
    const paleBlueSprite = createStarSprite(
        32,
        "rgba(235, 247, 255, 1)",
        "rgba(165, 212, 255, 0.72)",
        "rgba(105, 175, 245, 0.15)"
    );

    // Bộ sinh số ngẫu nhiên xác định theo seed để bầu trời đồng nhất khi resize
    function createRng(seed) {
        let s = seed >>> 0;
        return function () {
            s = (s * 1664525 + 1013904223) >>> 0;
            return s / 4294967296;
        };
    }

    // Kiểm tra điểm có nằm gần vùng quầng dải Ngân Hà ở giữa phía dưới hay không
    function milkyWayDensity(nx, ny) {
        // Trục nghiêng nhẹ quanh lower-center (x ~ 0.50, y ~ 0.80)
        const dx = (nx - 0.52) * 1.15 + (ny - 0.82) * 0.42;
        const dy = (ny - 0.82) * 1.9 - (nx - 0.52) * 0.28;
        const dist2 = dx * dx * 3.8 + dy * dy * 7.5;
        return Math.exp(-dist2);
    }

    function buildStaticSkyAndStars() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        if (!baseCanvas) {
            baseCanvas = document.createElement("canvas");
            baseCtx = baseCanvas.getContext("2d", { alpha: false });
        }
        baseCanvas.width = canvas.width;
        baseCanvas.height = canvas.height;
        baseCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

        // 1. Nền bầu trời đêm xanh teal-navy sâu thẳm
        const skyGrad = baseCtx.createLinearGradient(0, 0, width * 0.15, height);
        skyGrad.addColorStop(0, "#020811");
        skyGrad.addColorStop(0.5, "#051624");
        skyGrad.addColorStop(0.84, "#092233");
        skyGrad.addColorStop(1, "#04111c");
        baseCtx.fillStyle = skyGrad;
        baseCtx.fillRect(0, 0, width, height);

        // Quầng chuyển sắc nhẹ vùng trung tâm dưới
        const horizonGlow = baseCtx.createRadialGradient(
            width * 0.5,
            height * 0.86,
            height * 0.02,
            width * 0.5,
            height * 0.82,
            Math.max(width, height) * 0.65
        );
        horizonGlow.addColorStop(0, "rgba(22, 66, 104, 0.50)");
        horizonGlow.addColorStop(0.45, "rgba(12, 40, 68, 0.26)");
        horizonGlow.addColorStop(1, "rgba(2, 8, 17, 0)");
        baseCtx.fillStyle = horizonGlow;
        baseCtx.fillRect(0, 0, width, height);

        // 2. Dải Ngân Hà xanh lam dịu nhẹ ở giữa phía dưới khung hình
        const mwBlobs = [
            { x: 0.50, y: 0.82, rx: 0.34, ry: 0.17, rot: -0.18, c0: "rgba(72, 138, 198, 0.24)", c1: "rgba(38, 92, 146, 0.10)" },
            { x: 0.43, y: 0.85, rx: 0.24, ry: 0.12, rot: -0.22, c0: "rgba(110, 175, 228, 0.19)", c1: "rgba(48, 108, 165, 0.07)" },
            { x: 0.59, y: 0.78, rx: 0.26, ry: 0.13, rot: -0.15, c0: "rgba(92, 158, 218, 0.20)", c1: "rgba(40, 96, 152, 0.08)" },
            { x: 0.51, y: 0.83, rx: 0.16, ry: 0.08, rot: -0.19, c0: "rgba(148, 204, 248, 0.17)", c1: "rgba(70, 135, 198, 0.05)" }
        ];

        mwBlobs.forEach((b) => {
            baseCtx.save();
            baseCtx.translate(width * b.x, height * b.y);
            baseCtx.rotate(b.rot);
            baseCtx.scale(1, b.ry / b.rx);
            const radius = width * b.rx;
            const g = baseCtx.createRadialGradient(0, 0, 0, 0, 0, radius);
            g.addColorStop(0, b.c0);
            g.addColorStop(0.5, b.c1);
            g.addColorStop(1, "rgba(0, 0, 0, 0)");
            baseCtx.fillStyle = g;
            baseCtx.beginPath();
            baseCtx.arc(0, 0, radius, 0, TWO_PI);
            baseCtx.fill();
            baseCtx.restore();
        });

        // Dải bụi vũ trụ tối tinh tế (cosmic dust lanes) cắt nhẹ qua lõi Ngân Hà
        const dustLanes = [
            { x: 0.48, y: 0.83, rx: 0.22, ry: 0.045, rot: -0.17, a: 0.34 },
            { x: 0.56, y: 0.80, rx: 0.16, ry: 0.035, rot: -0.21, a: 0.26 }
        ];
        dustLanes.forEach((d) => {
            baseCtx.save();
            baseCtx.translate(width * d.x, height * d.y);
            baseCtx.rotate(d.rot);
            baseCtx.scale(1, d.ry / d.rx);
            const radius = width * d.rx;
            const g = baseCtx.createRadialGradient(0, 0, 0, 0, 0, radius);
            g.addColorStop(0, "rgba(2, 9, 18, " + d.a + ")");
            g.addColorStop(0.65, "rgba(2, 9, 18, " + (d.a * 0.4) + ")");
            g.addColorStop(1, "rgba(2, 9, 18, 0)");
            baseCtx.fillStyle = g;
            baseCtx.beginPath();
            baseCtx.arc(0, 0, radius, 0, TWO_PI);
            baseCtx.fill();
            baseCtx.restore();
        });

        // 3. Hàng nghìn ngôi sao siêu nhỏ cố định (static starfield + milky way dust stars)
        const rand = createRng(382026);
        const areaScale = Math.min(Math.max((width * height) / (1440 * 900), 0.55), 1.7);
        const staticCount = Math.round(1800 * areaScale);

        for (let i = 0; i < staticCount; i++) {
            let nx = rand();
            let ny = rand();
            // Khoảng 35% sao tập trung nhẹ quanh vùng dải Ngân Hà ở dưới giữa
            if (i % 3 === 0) {
                const angle = rand() * TWO_PI;
                const spread = Math.pow(rand(), 1.4);
                nx = 0.52 + Math.cos(angle) * spread * 0.34;
                ny = 0.81 + Math.sin(angle) * spread * 0.17 - (nx - 0.52) * 0.18;
            }
            if (nx < 0 || nx > 1 || ny < 0 || ny > 1) continue;

            const mw = milkyWayDensity(nx, ny);
            const r = 0.42 + Math.pow(rand(), 2.4) * 0.95;
            const alpha = (0.22 + Math.pow(rand(), 2.0) * 0.58) * (1 + mw * 0.5);
            const isPaleBlue = rand() < 0.42;

            baseCtx.fillStyle = isPaleBlue
                ? "rgba(186, 222, 255, " + Math.min(0.88, alpha).toFixed(3) + ")"
                : "rgba(244, 248, 255, " + Math.min(0.88, alpha).toFixed(3) + ")";
            baseCtx.beginPath();
            baseCtx.arc(nx * width, ny * height, r, 0, TWO_PI);
            baseCtx.fill();
        }

        // 4. Hạt nhiễu ảnh thiên văn siêu mịn (astrophotography fine grain)
        const tileSize = 128;
        const grainTile = document.createElement("canvas");
        grainTile.width = tileSize;
        grainTile.height = tileSize;
        const gctx = grainTile.getContext("2d");
        const imgData = gctx.createImageData(tileSize, tileSize);
        const data = imgData.data;
        for (let p = 0; p < data.length; p += 4) {
            const v = Math.floor(110 + (rand() - 0.5) * 90);
            data[p] = v;
            data[p + 1] = v + 6;
            data[p + 2] = v + 14;
            data[p + 3] = 10; // ~4% opacity nhẹ giữ độ trong
        }
        gctx.putImageData(imgData, 0, 0);
        const grainPattern = baseCtx.createPattern(grainTile, "repeat");
        if (grainPattern) {
            baseCtx.fillStyle = grainPattern;
            baseCtx.fillRect(0, 0, width, height);
        }

        // 5. Tập sao nhấp nháy êm dịu tại chỗ (~850 ngôi sao trắng & xanh nhạt)
        const twinkleCount = Math.round(850 * areaScale);
        twinklingStars = [];
        for (let i = 0; i < twinkleCount; i++) {
            let nx = rand();
            let ny = rand();
            if (i % 4 === 0) {
                const angle = rand() * TWO_PI;
                const spread = Math.pow(rand(), 1.25);
                nx = 0.52 + Math.cos(angle) * spread * 0.36;
                ny = 0.81 + Math.sin(angle) * spread * 0.18 - (nx - 0.52) * 0.18;
            }
            if (nx < 0 || nx > 1 || ny < 0 || ny > 1) continue;

            // Tần số nguyên thấp (1..4 chu kỳ / 25s) cho nhịp lấp lánh chậm rãi, êm dịu
            const freq1 = 1 + Math.floor(rand() * 3);
            const freq2 = 2 + Math.floor(rand() * 3);
            const isBright = rand() > 0.84;

            twinklingStars.push({
                x: nx * width,
                y: ny * height,
                radius: isBright ? 1.15 + rand() * 0.80 : 0.60 + rand() * 0.78,
                isPaleBlue: rand() < 0.45,
                isBright,
                freq1,
                freq2,
                phase1: rand() * TWO_PI,
                phase2: rand() * TWO_PI,
                minAlpha: isBright ? 0.50 + rand() * 0.20 : 0.28 + rand() * 0.24,
                ampAlpha: isBright ? 0.45 : 0.36 + rand() * 0.26
            });
        }
    }

    function spawnShootingStar(nowMs) {
        if (width <= 0 || height <= 0 || shootingStars.length >= 2) return;
        const angle = 2.53 + Math.random() * 0.30;
        const dist = Math.min(Math.max(Math.min(width, height) * (0.28 + Math.random() * 0.24), 220), 500);
        shootingStars.push({
            x0: width * (0.15 + Math.random() * 0.80),
            y0: height * (0.04 + Math.random() * 0.42),
            dx: Math.cos(angle),
            dy: Math.sin(angle),
            dist,
            tailMax: dist * (0.28 + Math.random() * 0.10),
            startMs: nowMs,
            duration: 850 + Math.random() * 600,
            width: 1.35 + Math.random() * 0.75,
            headSize: 9 + Math.random() * 6,
            isPaleBlue: Math.random() < 0.55,
            peakAlpha: 0.78 + Math.random() * 0.22
        });
    }

    function drawShootingStars(nowMs) {
        if (nextMeteorTime === 0) {
            nextMeteorTime = nowMs + 1800 + Math.random() * 800;
        }
        if (nowMs >= nextMeteorTime) {
            spawnShootingStar(nowMs);
            nextMeteorTime = nowMs + 3500 + Math.random() * 4000;
        }
        if (shootingStars.length === 0) return;

        ctx.lineCap = "round";
        for (let i = shootingStars.length - 1; i >= 0; i--) {
            const m = shootingStars[i];
            const elapsed = nowMs - m.startMs;
            if (elapsed >= m.duration) {
                shootingStars.splice(i, 1);
                continue;
            }
            if (elapsed < 0) continue;

            const t = elapsed / m.duration;
            const ease = 1 - Math.pow(1 - t, 1.85);
            const travel = m.dist * ease;
            const hx = m.x0 + m.dx * travel;
            const hy = m.y0 + m.dy * travel;

            let envelope = 1;
            if (t < 0.16) {
                envelope = t / 0.16;
            } else if (t > 0.55) {
                const fade = 1 - (t - 0.55) / 0.45;
                envelope = fade * fade;
            }
            const alpha = Math.min(1, Math.max(0, envelope * m.peakAlpha));
            if (alpha <= 0.01) continue;

            const shrink = t > 0.72 ? Math.max(0.22, 1 - (t - 0.72) * 2.3) : 1;
            const tailLen = Math.min(travel, m.dist * (0.28 + 0.12 * Math.sin(t * Math.PI)) * shrink);
            const tx = hx - m.dx * tailLen;
            const ty = hy - m.dy * tailLen;

            if (tailLen >= 1.5) {
                ctx.globalAlpha = 1;
                const bloomGrad = ctx.createLinearGradient(tx, ty, hx, hy);
                bloomGrad.addColorStop(0, "rgba(130, 198, 255, 0)");
                bloomGrad.addColorStop(1, "rgba(130, 198, 255, " + (0.20 * alpha).toFixed(3) + ")");
                ctx.strokeStyle = bloomGrad;
                ctx.lineWidth = m.width * 3.0;
                ctx.beginPath();
                ctx.moveTo(tx, ty);
                ctx.lineTo(hx, hy);
                ctx.stroke();

                const coreGrad = ctx.createLinearGradient(tx, ty, hx, hy);
                coreGrad.addColorStop(0, "rgba(155, 212, 255, 0)");
                coreGrad.addColorStop(0.55, "rgba(175, 224, 255, " + (0.45 * alpha).toFixed(3) + ")");
                coreGrad.addColorStop(1, "rgba(248, 252, 255, " + (0.95 * alpha).toFixed(3) + ")");
                ctx.strokeStyle = coreGrad;
                ctx.lineWidth = m.width;
                ctx.beginPath();
                ctx.moveTo(tx, ty);
                ctx.lineTo(hx, hy);
                ctx.stroke();
            }

            const headDiameter = m.headSize * (0.65 + 0.35 * alpha);
            ctx.globalAlpha = Math.min(1, alpha * 0.95);
            ctx.drawImage(
                m.isPaleBlue ? paleBlueSprite : whiteSprite,
                hx - headDiameter * 0.5,
                hy - headDiameter * 0.5,
                headDiameter,
                headDiameter
            );
        }
        ctx.globalAlpha = 1;
        ctx.lineCap = "butt";
    }

    function drawFrame(nowMs) {
        if (!baseCanvas) return;
        if (!startTime) startTime = nowMs;

        const elapsedSec = ((nowMs - startTime) * 0.001) % LOOP_SECONDS;
        const loopAngle = (elapsedSec / LOOP_SECONDS) * TWO_PI;

        ctx.globalCompositeOperation = "source-over";
        ctx.globalAlpha = 1;
        ctx.drawImage(baseCanvas, 0, 0, width, height);

        for (let i = 0; i < twinklingStars.length; i++) {
            const s = twinklingStars[i];
            const waveA = 0.5 + 0.5 * Math.sin(loopAngle * s.freq1 + s.phase1);
            const waveB = 0.5 + 0.5 * Math.sin(loopAngle * s.freq2 + s.phase2);
            const pulse = waveA * 0.68 + waveB * 0.32;
            const alpha = Math.min(1, s.minAlpha + pulse * s.ampAlpha);

            if (s.isBright) {
                const glowDiameter = s.radius * (5.2 + pulse * 1.8);
                ctx.globalAlpha = alpha;
                ctx.drawImage(
                    s.isPaleBlue ? paleBlueSprite : whiteSprite,
                    s.x - glowDiameter * 0.5,
                    s.y - glowDiameter * 0.5,
                    glowDiameter,
                    glowDiameter
                );
            } else {
                ctx.globalAlpha = alpha;
                ctx.fillStyle = s.isPaleBlue ? "#cbe6ff" : "#f7fbff";
                ctx.fillRect(s.x - s.radius * 0.5, s.y - s.radius * 0.5, s.radius * 1.1, s.radius * 1.1);
            }
        }
        ctx.globalAlpha = 1;

        if (!reducedMotion) {
            drawShootingStars(nowMs);
        }
    }

    function tick(nowMs) {
        if (!running) return;
        if (!lastDrawTime || nowMs - lastDrawTime >= FRAME_INTERVAL) {
            lastDrawTime = nowMs;
            drawFrame(nowMs);
        }
        rafId = window.requestAnimationFrame(tick);
    }

    let resizeTimer = null;
    window.addEventListener("resize", () => {
        if (!running && !baseCanvas) return;
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            shootingStars = [];
            nextMeteorTime = 0;
            buildStaticSkyAndStars();
            if (running) {
                drawFrame(performance.now());
            }
        }, 150);
    });

    window.NightSkyBg = {
        start() {
            if (running) return;
            running = true;
            shootingStars = [];
            nextMeteorTime = 0;
            buildStaticSkyAndStars();
            startTime = 0;
            lastDrawTime = 0;
            if (reducedMotion) {
                drawFrame(performance.now());
            } else {
                drawFrame(performance.now());
                rafId = window.requestAnimationFrame(tick);
            }
        },
        stop() {
            running = false;
            shootingStars = [];
            nextMeteorTime = 0;
            if (rafId !== null) {
                window.cancelAnimationFrame(rafId);
                rafId = null;
            }
        }
    };

    if ((document.documentElement.getAttribute("data-theme") || "dark") === "dark") {
        window.NightSkyBg.start();
    }
})();
