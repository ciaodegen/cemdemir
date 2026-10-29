// Usage: node render.js specs.json outdir
// spec: {name, char, yaw, headYaw, headPitch, mouth, blink, smile, loupe, gaze:[x,y], brow, w, h, view:[cx,cy,halfH,dist]}
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const specs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const outdir = process.argv[3];
  const frag = fs.readFileSync(path.join(__dirname, 'char.frag'), 'utf8');
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage();
  await p.setContent('<canvas id=c></canvas>');
  await p.evaluate((frag) => {
    const c = document.getElementById('c');
    const gl = c.getContext('webgl2', { preserveDrawingBuffer: true, premultipliedAlpha: false, antialias: false });
    const vs = '#version 300 es\nin vec2 p; void main(){gl_Position=vec4(p,0,1);}';
    function sh(t, s) { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; }
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, frag)); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
    gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    window.R = (s) => {
      c.width = s.w; c.height = s.h; gl.viewport(0, 0, s.w, s.h);
      const u = (n) => gl.getUniformLocation(pr, n);
      gl.uniform2f(u('uRes'), s.w, s.h);
      gl.uniform1i(u('uChar'), s.char);
      gl.uniform1f(u('uYaw'), s.yaw || 0); gl.uniform1f(u('uHeadYaw'), s.headYaw || 0); gl.uniform1f(u('uHeadPitch'), s.headPitch || 0);
      gl.uniform1f(u('uMouth'), s.mouth || 0); gl.uniform1f(u('uBlink'), s.blink || 0); gl.uniform1f(u('uSmile'), s.smile || 0);
      gl.uniform1f(u('uLoupe'), s.loupe || 0); gl.uniform1f(u('uBrow'), s.brow || 0);
      gl.uniform2f(u('uGaze'), (s.gaze || [0, 0])[0], (s.gaze || [0, 0])[1]);
      const v = s.view || [0, 0.5, 0.62, 4.0]; gl.uniform4f(u('uView'), v[0], v[1], v[2], v[3]);
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      const px = new Uint8Array(1); gl.readPixels(0, 0, 1, 1, gl.ALPHA, gl.UNSIGNED_BYTE, new Uint8Array(4));
      return c.toDataURL('image/png');
    };
  }, frag);
  for (const s of specs) {
    const out = path.join(outdir, s.name + '.png');
    if (fs.existsSync(out) && !s.force) continue;
    const t0 = Date.now();
    const url = await p.evaluate((s) => window.R(s), s);
    fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
    console.log(s.name, ((Date.now() - t0) / 1000).toFixed(1) + 's');
  }
  await b.close();
})().catch(e => { console.error(e.message || e); process.exit(1); });
