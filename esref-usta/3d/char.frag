#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 uRes;
uniform int uChar;          // 0 esref, 1 deniz, 2 emre
uniform float uYaw;         // body yaw (rad), + turns toward screen right
uniform float uHeadYaw;     // extra head yaw
uniform float uHeadPitch;   // + looks down
uniform float uMouth;       // 0..1
uniform float uBlink;       // 0 open .. 1 closed
uniform float uSmile;       // 0..1
uniform float uLoupe;       // 0..1 (esref)
uniform vec2 uGaze;         // pupil offset (-1..1)
uniform float uBrow;        // + raised, - frown
uniform vec4 uView;         // cx, cy, halfHeight, camDist

#define PI 3.14159265

float smin(float a, float b, float k){ float h = max(k - abs(a - b), 0.0) / k; return min(a, b) - h * h * k * 0.25; }
float smax(float a, float b, float k){ return -smin(-a, -b, k); }
float sdE(vec3 p, vec3 r){ float k0 = length(p / r); float k1 = length(p / (r * r)); return k0 * (k0 - 1.0) / max(k1, 1e-6); }
float sdC(vec3 p, vec3 a, vec3 b, float r){ vec3 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0); return length(pa - ba * h) - r; }
float sdTz(vec3 p, float R, float r){ vec2 q = vec2(length(p.xy) - R, p.z); return length(q) - r; }
float sdCylZ(vec3 p, float r, float h){ vec2 d = abs(vec2(length(p.xy), p.z)) - vec2(r, h); return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)); }
float sdBox(vec3 p, vec3 b){ vec3 q = abs(p) - b; return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0); }
mat3 rotY(float a){ float c = cos(a), s = sin(a); return mat3(c, 0, -s, 0, 1, 0, s, 0, c); }
mat3 rotX(float a){ float c = cos(a), s = sin(a); return mat3(1, 0, 0, 0, c, s, 0, -s, c); }
float curl(vec3 p, float f){ return sin(p.x * f) * sin(p.y * f * 1.1 + 1.3) * sin(p.z * f * 0.9 + 0.7); }

vec3 bodySpace(vec3 p){ return rotY(-uYaw) * p; }
const float HS = 1.28;  // cartoon head scale
vec3 headSpace(vec3 b, vec3 pivot){ return (rotX(uHeadPitch) * (rotY(-uHeadYaw) * (b - pivot))) / HS + pivot; }

// material ids
const float M_SKIN = 1., M_WHITEHAIR = 2., M_EYE = 3., M_PUPIL = 4., M_GLASS = 5., M_SHIRT_G = 6., M_APRON = 7.,
            M_MOUTH = 8., M_METAL = 10., M_BLACKHAIR = 11., M_TEAL = 12., M_DENIM = 13., M_NAVY = 14., M_SWEATER = 15.,
            M_RED = 16., M_NOSE = 17., M_IRIS = 18., M_LOUPE = 20., M_BROW_D = 21., M_LENS = 22.;

vec2 U(vec2 a, vec2 b){ return a.x < b.x ? a : b; }

// ---------- shared face parts ----------
vec2 eyes(vec3 h, vec3 hc, float ex, float ey, float ez, float r, float irisR, bool iris, float lidRest){
  vec2 res = vec2(1e9, 0.);
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    vec3 c = hc + vec3(sx * ex, ey, ez);
    float ball = length(h - c) - r;
    res = U(res, vec2(ball, M_EYE));
    vec3 g = normalize(vec3(uGaze.x * 0.35, uGaze.y * 0.3, 1.0));
    vec3 pc = c + g * (r - irisR * 0.8);
    if (iris) {
      res = U(res, vec2(length(h - pc) - irisR, M_IRIS));
      res = U(res, vec2(length(h - (c + g * (r - irisR * 0.5))) - irisR * 0.55, M_PUPIL));
    } else {
      res = U(res, vec2(length(h - pc) - irisR, M_PUPIL));
    }
    // upper lid: skin cap over the eyeball, its lower edge drops with blink
    float lidY = mix(c.y + lidRest, c.y - r * 1.1, uBlink);
    float lid = max(length(h - c) - r * 1.12, lidY - h.y);
    res = U(res, vec2(lid, M_SKIN));
  }
  return res;
}

// ---------- Eşref ----------
const vec4 ESREF_CURLS[22] = vec4[22](
  vec4(-0.12, 0.08, -0.02, 0.065), vec4(0.12, 0.08, -0.02, 0.065), vec4(-0.14, 0.0, -0.04, 0.06), vec4(0.14, 0.0, -0.04, 0.06),
  vec4(-0.08, 0.13, 0.02, 0.06), vec4(0.08, 0.13, 0.02, 0.06), vec4(0.0, 0.15, 0.0, 0.06), vec4(-0.04, 0.14, 0.07, 0.05),
  vec4(0.05, 0.14, 0.07, 0.05), vec4(0.0, 0.13, -0.08, 0.07), vec4(-0.09, 0.09, -0.1, 0.07), vec4(0.09, 0.09, -0.1, 0.07),
  vec4(-0.13, -0.05, -0.07, 0.055), vec4(0.13, -0.05, -0.07, 0.055), vec4(0.0, 0.05, -0.14, 0.07), vec4(-0.07, -0.02, -0.13, 0.06),
  vec4(0.07, -0.02, -0.13, 0.06), vec4(-0.11, 0.12, 0.06, 0.04), vec4(0.11, 0.12, 0.06, 0.04), vec4(-0.15, 0.07, 0.03, 0.04),
  vec4(0.15, 0.07, 0.03, 0.04), vec4(0.0, 0.17, 0.05, 0.045)
);

vec2 esref(vec3 p){
  vec3 b = bodySpace(p);
  vec2 res = vec2(1e9, 0.);
  // torso + shoulders (stout)
  float torso = sdE(b - vec3(0., 0.25, 0.), vec3(0.27, 0.37, 0.2));
  float sh = sdE(b - vec3(0., 0.5, -0.01), vec3(0.31, 0.13, 0.17));
  float body = smin(torso, sh, 0.08);
  // arms resting toward the counter
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float ua = sdC(b, vec3(sx * 0.27, 0.5, -0.01), vec3(sx * 0.33, 0.22, 0.05), 0.075);
    body = smin(body, ua, 0.04);
    float cuff = sdC(b, vec3(sx * 0.33, 0.25, 0.045), vec3(sx * 0.335, 0.19, 0.07), 0.083);
    res = U(res, vec2(cuff, M_SHIRT_G + 0.5));
    float fa = sdC(b, vec3(sx * 0.335, 0.19, 0.07), vec3(sx * 0.24, 0.02, 0.22), 0.058);
    float hand = sdE(b - vec3(sx * 0.21, 0.0, 0.26), vec3(0.062, 0.045, 0.075));
    res = U(res, vec2(smin(fa, hand, 0.03), M_SKIN));
  }
  res = U(res, vec2(body, M_SHIRT_G));
  // apron: bib + skirt on the front
  float ap = sdE(b - vec3(0., 0.24, 0.0), vec3(0.283, 0.385, 0.214));
  ap = max(ap, 0.035 - b.z);
  ap = max(ap, b.y - 0.43);
  ap = max(ap, abs(b.x) - (0.17 + max(0.0, 0.25 - b.y) * 0.35));
  float straps = min(sdC(b, vec3(-0.15, 0.42, 0.15), vec3(-0.16, 0.6, -0.01), 0.018), sdC(b, vec3(0.15, 0.42, 0.15), vec3(0.16, 0.6, -0.01), 0.018));
  straps = min(straps, sdC(b, vec3(-0.16, 0.6, -0.01), vec3(0.12, 0.3, -0.2), 0.018));
  straps = min(straps, sdC(b, vec3(0.16, 0.6, -0.01), vec3(-0.12, 0.3, -0.2), 0.018));
  float pocket = sdBox(b - vec3(0., 0.29, 0.212), vec3(0.08, 0.055, 0.01)) - 0.005;
  res = U(res, vec2(min(min(ap, straps), pocket), M_APRON));
  float wrench = min(sdC(b, vec3(0.12, 0.06, 0.225), vec3(0.135, 0.3, 0.215), 0.011), length(b - vec3(0.137, 0.32, 0.214)) - 0.024);

  // head
  vec3 pivot = vec3(0., 0.6, 0.0);
  vec3 h = headSpace(b, pivot);
  vec2 hr = vec2(1e9, 0.);
  vec3 hc = vec3(0., 0.82, 0.03);
  float skull = sdE(h - hc, vec3(0.15, 0.16, 0.145));
  float cheeks = min(length(h - (hc + vec3(-0.072, -0.05, 0.09))) - 0.06, length(h - (hc + vec3(0.072, -0.05, 0.09))) - 0.06);
  skull = smin(skull, cheeks, 0.04);
  float ears = min(sdE(h - (hc + vec3(-0.148, -0.005, 0.0)), vec3(0.022, 0.042, 0.026)), sdE(h - (hc + vec3(0.148, -0.005, 0.0)), vec3(0.022, 0.042, 0.026)));
  skull = smin(skull, ears, 0.015);
  // mouth cavity
  vec3 mq = h - (hc + vec3(0., -0.092, 0.15));
  float mouthCav = sdE(mq, vec3(0.034, 0.004 + 0.022 * uMouth, 0.06));
  hr = U(hr, vec2(skull, M_SKIN));
  float nose = sdE(h - (hc + vec3(0., -0.025, 0.152)), vec3(0.046, 0.04, 0.042));
  hr = U(hr, vec2(nose, M_NOSE));
  hr = U(hr, eyes(h, hc, 0.056, 0.02, 0.108, 0.03, 0.016, false, 0.016));
  // brows (bushy)
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float by = 0.07 + uBrow * 0.012;
    float brow = sdC(h, hc + vec3(sx * 0.022, by - 0.004, 0.14), hc + vec3(sx * 0.098, by + 0.004, 0.11), 0.019);
    brow += 0.003 * curl(h, 80.);
    hr = U(hr, vec2(brow, M_WHITEHAIR + 0.3));
  }
  // glasses
  float gl = 1e9;
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    vec3 gc = hc + vec3(sx * 0.058, 0.02, 0.152);
    gl = min(gl, sdTz(h - gc, 0.043, 0.0042));
    gl = min(gl, sdC(h, gc + vec3(sx * 0.043, 0.0, -0.005), hc + vec3(sx * 0.15, 0.025, 0.0), 0.0035));
  }
  gl = min(gl, sdC(h, hc + vec3(-0.016, 0.03, 0.158), hc + vec3(0.016, 0.03, 0.158), 0.0035));
  hr = U(hr, vec2(gl, M_GLASS));
  // mustache
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    vec3 q = h - (hc + vec3(sx * 0.04, -0.068, 0.15));
    float a = sx * 0.38; float c = cos(a), sn = sin(a);
    q.xy = mat2(c, -sn, sn, c) * q.xy;
    float m = sdE(q, vec3(0.058, 0.026, 0.034)) + 0.003 * curl(h, 60.);
    hr = U(hr, vec2(m, M_WHITEHAIR));
  }
  // beard
  float beard = sdE(h - (hc + vec3(0., -0.135, 0.065)), vec3(0.135, 0.125, 0.105));
  beard = smin(beard, length(h - (hc + vec3(-0.1, -0.07, 0.05))) - 0.075, 0.04);
  beard = smin(beard, length(h - (hc + vec3(0.1, -0.07, 0.05))) - 0.075, 0.04);
  beard = smin(beard, sdE(h - (hc + vec3(0., -0.2, 0.06)), vec3(0.08, 0.07, 0.07)), 0.05);
  beard += 0.006 * curl(h, 34.) + 0.002 * curl(h, 85.);
  beard = smax(beard, -mouthCav, 0.006);
  hr = U(hr, vec2(beard, M_WHITEHAIR));
  hr = U(hr, vec2(sdE(mq + vec3(0., 0., 0.02), vec3(0.03, 0.003 + 0.02 * uMouth, 0.03)), M_MOUTH));
  // hair curls
  float hair = 1e9;
  for (int i = 0; i < 22; i++) {
    vec4 cv = ESREF_CURLS[i];
    hair = smin(hair, length(h - (hc + cv.xyz)) - cv.w, 0.025);
  }
  hair += 0.009 * curl(h, 38.) + 0.0025 * curl(h, 90.);
  hr = U(hr, vec2(hair, M_WHITEHAIR));
  // loupe on the right eye
  if (uLoupe > 0.01) {
    vec3 lc = hc + vec3(0.058, 0.02 + (1.0 - uLoupe) * 0.25, 0.2);
    float lbody = sdCylZ(h - lc, 0.034, 0.035) - 0.004;
    float lens = sdCylZ(h - (lc + vec3(0., 0., 0.038)), 0.026, 0.004);
    hr = U(hr, vec2(lbody, M_LOUPE));
    hr = U(hr, vec2(lens, M_LENS));
  }
  res = U(res, vec2(hr.x * HS, hr.y));
  return res;
}

// ---------- Deniz ----------
const vec4 DENIZ_TUFTS[18] = vec4[18](
  vec4(0.0, 0.13, 0.06, 0.06), vec4(-0.07, 0.12, 0.05, 0.055), vec4(0.07, 0.12, 0.05, 0.055), vec4(-0.11, 0.07, 0.03, 0.05),
  vec4(0.11, 0.07, 0.03, 0.05), vec4(0.0, 0.14, -0.03, 0.065), vec4(-0.08, 0.11, -0.07, 0.06), vec4(0.08, 0.11, -0.07, 0.06),
  vec4(0.0, 0.08, -0.11, 0.07), vec4(-0.12, 0.02, -0.06, 0.05), vec4(0.12, 0.02, -0.06, 0.05), vec4(-0.04, 0.1, 0.1, 0.04),
  vec4(0.04, 0.095, 0.105, 0.038), vec4(-0.1, 0.1, 0.07, 0.04), vec4(0.1, 0.1, 0.07, 0.04), vec4(0.03, 0.17, 0.02, 0.04),
  vec4(-0.05, 0.16, -0.01, 0.04), vec4(0.0, 0.03, -0.13, 0.06)
);

vec2 deniz(vec3 p){
  vec3 b = bodySpace(p);
  vec2 res = vec2(1e9, 0.);
  float torso = sdE(b - vec3(0., 0.26, 0.), vec3(0.2, 0.34, 0.135));
  float sh = sdE(b - vec3(0., 0.5, -0.005), vec3(0.24, 0.1, 0.125));
  float body = smin(torso, sh, 0.06);
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float sleeve = sdC(b, vec3(sx * 0.21, 0.5, -0.005), vec3(sx * 0.255, 0.33, 0.02), 0.066);
    body = smin(body, sleeve, 0.03);
    float ua = sdC(b, vec3(sx * 0.255, 0.33, 0.02), vec3(sx * 0.27, 0.2, 0.05), 0.048);
    float fa = sdC(b, vec3(sx * 0.27, 0.2, 0.05), vec3(sx * 0.2, 0.02, 0.2), 0.043);
    float hand = sdE(b - vec3(sx * 0.18, 0.0, 0.23), vec3(0.048, 0.036, 0.062));
    res = U(res, vec2(smin(smin(ua, fa, 0.02), hand, 0.02), M_SKIN));
  }
  res = U(res, vec2(body, M_TEAL));
  float neck = sdC(b, vec3(0., 0.52, 0.0), vec3(0., 0.66, 0.01), 0.048);
  res = U(res, vec2(neck, M_SKIN));
  // overalls: lower wrap + bib + straps
  float ov = sdE(b - vec3(0., 0.25, 0.0), vec3(0.207, 0.345, 0.142));
  float lower = max(ov, b.y - 0.13);
  float bib = max(max(max(ov, 0.02 - b.z), b.y - 0.4), abs(b.x) - 0.13);
  float straps = min(sdC(b, vec3(-0.11, 0.39, 0.12), vec3(-0.13, 0.56, -0.01), 0.017), sdC(b, vec3(0.11, 0.39, 0.12), vec3(0.13, 0.56, -0.01), 0.017));
  straps = min(straps, min(sdC(b, vec3(-0.13, 0.56, -0.01), vec3(0.0, 0.3, -0.15), 0.017), sdC(b, vec3(0.13, 0.56, -0.01), vec3(0.0, 0.3, -0.15), 0.017)));
  float pocket = sdBox(b - vec3(0., 0.29, 0.142), vec3(0.065, 0.05, 0.008)) - 0.004;
  res = U(res, vec2(min(min(lower, bib), min(straps, pocket)), M_DENIM));
  float buttons = min(length(b - vec3(-0.11, 0.385, 0.128)) - 0.013, length(b - vec3(0.11, 0.385, 0.128)) - 0.013);
  res = U(res, vec2(buttons, M_METAL));
  res = U(res, vec2(sdC(b, vec3(0.04, 0.3, 0.152), vec3(0.045, 0.37, 0.15), 0.007), M_RED));

  vec3 pivot = vec3(0., 0.62, 0.0);
  vec3 h = headSpace(b, pivot);
  vec2 hr = vec2(1e9, 0.);
  vec3 hc = vec3(0., 0.79, 0.02);
  float skull = sdE(h - hc, vec3(0.122, 0.142, 0.128));
  float jaw = sdE(h - (hc + vec3(0., -0.07, 0.03)), vec3(0.095, 0.085, 0.1));
  skull = smin(skull, jaw, 0.05);
  float ears = min(sdE(h - (hc + vec3(-0.122, -0.01, -0.005)), vec3(0.02, 0.036, 0.024)), sdE(h - (hc + vec3(0.122, -0.01, -0.005)), vec3(0.02, 0.036, 0.024)));
  skull = smin(skull, ears, 0.012);
  vec3 mq = h - (hc + vec3(0., -0.082, 0.118));
  mq.y -= 9.0 * mq.x * mq.x * (0.4 + uSmile);
  float mouthCav = sdE(mq, vec3(0.03, 0.0035 + 0.017 * uMouth, 0.05));
  skull = smax(skull, -mouthCav, 0.005);
  hr = U(hr, vec2(skull, M_SKIN));
  hr = U(hr, vec2(sdE(mq + vec3(0., 0., 0.016), vec3(0.028, 0.003 + 0.016 * uMouth, 0.03)), M_MOUTH));
  hr = U(hr, vec2(sdE(h - (hc + vec3(0., -0.025, 0.128)), vec3(0.021, 0.034, 0.028)), M_SKIN));
  hr = U(hr, eyes(h, hc, 0.05, 0.012, 0.094, 0.033, 0.021, true, 0.026));
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float by = 0.058 + uBrow * 0.012;
    float brow = sdC(h, hc + vec3(sx * 0.02, by - 0.003, 0.118), hc + vec3(sx * 0.088, by + 0.006, 0.097), 0.011);
    hr = U(hr, vec2(brow, M_BROW_D));
  }
  float hair = sdE(h - (hc + vec3(0., 0.035, -0.012)), vec3(0.134, 0.135, 0.138));
  hair = smax(hair, (hc.y + 0.045) - h.y - 0.35 * max(0.0, -(h.z - hc.z)), 0.03);
  for (int i = 0; i < 18; i++) {
    vec4 tv = DENIZ_TUFTS[i];
    vec3 q = h - (hc + tv.xyz);
    hair = smin(hair, sdE(q, vec3(tv.w * 1.15, tv.w * 0.75, tv.w)), 0.02);
  }
  hair += 0.007 * curl(h, 45.);
  hr = U(hr, vec2(hair, M_BLACKHAIR));
  res = U(res, vec2(hr.x * HS, hr.y));
  return res;
}

// ---------- Emre ----------
vec2 emre(vec3 p){
  vec3 b = bodySpace(p);
  vec2 res = vec2(1e9, 0.);
  float torso = sdE(b - vec3(0., 0.25, 0.), vec3(0.23, 0.36, 0.155));
  float sh = sdE(b - vec3(0., 0.5, -0.005), vec3(0.27, 0.115, 0.14));
  float body = smin(torso, sh, 0.07);
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float ua = sdC(b, vec3(sx * 0.24, 0.5, -0.005), vec3(sx * 0.29, 0.22, 0.05), 0.068);
    float fa = sdC(b, vec3(sx * 0.29, 0.22, 0.05), vec3(sx * 0.2, 0.04, 0.22), 0.058);
    body = smin(body, min(ua, fa), 0.03);
    float hand = sdE(b - vec3(sx * 0.18, 0.01, 0.25), vec3(0.05, 0.037, 0.064));
    res = U(res, vec2(hand, M_SKIN));
  }
  // collar
  float collar = sdTz(rotX(-1.35) * (b - vec3(0., 0.58, 0.0)), 0.085, 0.03);
  body = smin(body, collar, 0.02);
  res = U(res, vec2(body, M_NAVY));
  float sweater = sdC(b, vec3(0., 0.5, 0.06), vec3(0., 0.62, 0.0), 0.06);
  res = U(res, vec2(sweater, M_SWEATER));
  vec3 pivot = vec3(0., 0.62, 0.0);
  vec3 h = headSpace(b, pivot);
  vec2 hr = vec2(1e9, 0.);
  vec3 hc = vec3(0., 0.8, 0.02);
  float skull = sdE(h - hc, vec3(0.124, 0.142, 0.13));
  float jaw = sdE(h - (hc + vec3(0., -0.072, 0.03)), vec3(0.1, 0.085, 0.1));
  skull = smin(skull, jaw, 0.05);
  float ears = min(sdE(h - (hc + vec3(-0.124, -0.01, -0.005)), vec3(0.02, 0.037, 0.024)), sdE(h - (hc + vec3(0.124, -0.01, -0.005)), vec3(0.02, 0.037, 0.024)));
  skull = smin(skull, ears, 0.012);
  vec3 mq = h - (hc + vec3(0., -0.085, 0.118));
  mq.y += (5.0 - 16.0 * uSmile) * mq.x * mq.x;
  float mouthCav = sdE(mq, vec3(0.029, 0.003 + 0.017 * uMouth, 0.05));
  skull = smax(skull, -mouthCav, 0.005);
  hr = U(hr, vec2(skull, M_SKIN + 0.4));
  hr = U(hr, vec2(sdE(mq + vec3(0., 0., 0.016), vec3(0.027, 0.003 + 0.016 * uMouth, 0.03)), M_MOUTH));
  hr = U(hr, vec2(sdE(h - (hc + vec3(0., -0.028, 0.13)), vec3(0.022, 0.036, 0.029)), M_SKIN));
  hr = U(hr, eyes(h, hc, 0.05, 0.012, 0.097, 0.03, 0.019, true, 0.012));
  for (int s = 0; s < 2; s++) {
    float sx = s == 0 ? -1.0 : 1.0;
    float by = 0.055 + uBrow * 0.012;
    float brow = sdC(h, hc + vec3(sx * 0.02, by + 0.004, 0.12), hc + vec3(sx * 0.088, by - 0.004, 0.1), 0.009);
    hr = U(hr, vec2(brow, M_BROW_D));
  }
  float hair = sdE(h - (hc + vec3(0., 0.03, -0.012)), vec3(0.133, 0.14, 0.138));
  hair = smax(hair, (hc.y + 0.06) - h.y - 0.45 * max(0.0, -(h.z - hc.z)), 0.03);
  hair = smin(hair, sdE(h - (hc + vec3(-0.03, 0.12, 0.06)), vec3(0.09, 0.04, 0.06)), 0.03);
  hair += 0.002 * curl(h, 120.);
  hr = U(hr, vec2(hair, M_BLACKHAIR + 0.5));
  res = U(res, vec2(hr.x * HS, hr.y));
  return res;
}

vec2 map(vec3 p){
  if (uChar == 0) return esref(p);
  if (uChar == 1) return deniz(p);
  return emre(p);
}

vec3 calcNormal(vec3 p){
  const float e = 0.0006;
  vec2 k = vec2(1, -1);
  return normalize(k.xyy * map(p + k.xyy * e).x + k.yyx * map(p + k.yyx * e).x + k.yxy * map(p + k.yxy * e).x + k.xxx * map(p + k.xxx * e).x);
}

float shadow(vec3 ro, vec3 rd){
  float res = 1.0, t = 0.01;
  for (int i = 0; i < 28; i++) {
    float h = map(ro + rd * t).x;
    res = min(res, 10.0 * h / t);
    t += clamp(h, 0.01, 0.08);
    if (res < 0.02 || t > 1.2) break;
  }
  return clamp(res, 0.0, 1.0);
}

float ao(vec3 p, vec3 n){
  float o = 0.0, s = 1.0;
  for (int i = 1; i <= 4; i++) {
    float h = 0.012 * float(i);
    o += (h - map(p + n * h).x) * s; s *= 0.7;
  }
  return clamp(1.0 - 4.0 * o, 0.0, 1.0);
}

vec3 albedo(float id, vec3 p, vec3 n){
  vec3 b = bodySpace(p);
  if (id < 1.5) {
    if (uChar == 2 && id > 1.3) {
      // stubble on Emre's jaw
      vec3 h = headSpace(b, vec3(0., 0.62, 0.));
      float jawm = smoothstep(0.75, 0.70, h.y) * smoothstep(0.02, 0.07, h.z);
      return mix(vec3(0.86, 0.58, 0.44), vec3(0.6, 0.45, 0.38), jawm * 0.55);
    }
    return uChar == 0 ? vec3(0.88, 0.55, 0.42) : vec3(0.86, 0.57, 0.42);
  }
  if (id < 2.1) return vec3(0.9, 0.88, 0.84);
  if (id < 2.5) return vec3(0.82, 0.8, 0.76);
  if (id < 3.5) return vec3(0.95, 0.94, 0.92);
  if (id < 4.5) return vec3(0.05, 0.04, 0.04);
  if (id < 5.5) return vec3(0.42, 0.28, 0.14);
  if (id < 6.1) return vec3(0.25, 0.31, 0.16);
  if (id < 6.9) return vec3(0.31, 0.37, 0.21);
  if (id < 7.5) {
    // leather apron with darker pocket stitching
    float g = 0.5 + 0.5 * sin(b.x * 90.0 + sin(b.y * 40.0) * 2.0);
    return mix(vec3(0.33, 0.17, 0.08), vec3(0.4, 0.22, 0.1), g * 0.5);
  }
  if (id < 8.5) return vec3(0.25, 0.06, 0.06);
  if (id < 10.5) return vec3(0.62, 0.64, 0.66);
  if (id < 11.3) return vec3(0.06, 0.05, 0.05);
  if (id < 11.7) return vec3(0.1, 0.075, 0.06);
  if (id < 12.5) return vec3(0.1, 0.3, 0.34);
  if (id < 13.5) {
    float g = 0.5 + 0.5 * sin(b.x * 300.0 + b.y * 300.0);
    return mix(vec3(0.2, 0.3, 0.5), vec3(0.25, 0.36, 0.56), g * 0.4);
  }
  if (id < 14.5) return vec3(0.09, 0.11, 0.2);
  if (id < 15.5) return vec3(0.5, 0.5, 0.5);
  if (id < 16.5) return vec3(0.7, 0.08, 0.06);
  if (id < 17.5) return vec3(0.95, 0.52, 0.42);
  if (id < 18.5) return vec3(0.36, 0.2, 0.1);
  if (id < 20.5) return vec3(0.06, 0.06, 0.07);
  if (id < 21.5) return vec3(0.07, 0.05, 0.04);
  return vec3(0.55, 0.65, 0.7);
}

void main(){
  vec2 frag = gl_FragCoord.xy;
  vec2 uv = (frag - 0.5 * uRes) / (0.5 * uRes.y);
  float camD = uView.w;
  vec3 ro = vec3(uView.x, uView.y, camD);
  vec3 rd = normalize(vec3(uv * uView.z / camD, -1.0));
  // bounding box
  vec3 bmin = vec3(-0.6, -0.15, -0.65), bmax = vec3(0.6, 1.4, 0.65);
  vec3 t0 = (bmin - ro) / rd, t1 = (bmax - ro) / rd;
  vec3 tn = min(t0, t1), tf = max(t0, t1);
  float tnear = max(max(tn.x, tn.y), tn.z), tfar = min(min(tf.x, tf.y), tf.z);
  if (tnear > tfar || tfar < 0.0) { fragColor = vec4(0.); return; }
  float t = max(tnear, 0.0);
  vec2 hit = vec2(-1.);
  for (int i = 0; i < 200; i++) {
    vec2 h = map(ro + rd * t);
    if (h.x < 0.0004 * t) { hit = vec2(t, h.y); break; }
    t += h.x * 0.75;
    if (t > tfar) break;
  }
  if (hit.x < 0.0) { fragColor = vec4(0.); return; }
  vec3 p = ro + rd * hit.x;
  vec3 n = calcNormal(p);
  vec3 alb = pow(albedo(hit.y, p, n), vec3(2.0));
  vec3 keyDir = normalize(vec3(-0.45, 0.85, 0.55));
  vec3 fillDir = normalize(vec3(0.8, 0.15, 0.7));
  vec3 rimDir = normalize(vec3(0.25, 0.5, -1.0));
  float sh = shadow(p + n * 0.002, keyDir);
  float a = ao(p, n);
  bool isSkin = hit.y < 1.5 || (hit.y > 16.5 && hit.y < 17.5);
  float wrap = isSkin ? 0.35 : 0.15;
  float dk = clamp((dot(n, keyDir) + wrap) / (1.0 + wrap), 0.0, 1.0);
  float df = clamp(dot(n, fillDir), 0.0, 1.0);
  float fres = pow(1.0 - clamp(dot(n, -rd), 0.0, 1.0), 3.0);
  float rim = clamp(dot(n, rimDir), 0.0, 1.0) * 0.6 + fres * 0.5;
  vec3 col = alb * (vec3(1.0, 0.8, 0.58) * 2.3 * dk * mix(0.2, 1.0, sh) + vec3(0.3, 0.36, 0.5) * 0.45 * df + vec3(0.2, 0.17, 0.14) * a);
  col += vec3(1.0, 0.75, 0.5) * rim * 0.28 * a;
  if (isSkin) col += vec3(0.25, 0.05, 0.02) * dk * 0.15;  // warm subsurface tint
  vec3 hv = normalize(keyDir - rd);
  float specK = (hit.y > 3.5 && hit.y < 5.5) || (hit.y > 19.5 && hit.y < 20.5) || hit.y > 21.5 ? 0.9 : (hit.y > 10.5 && hit.y < 11.8 ? 0.12 : (hit.y > 17.5 && hit.y < 18.5 ? 0.6 : 0.1));
  col += vec3(1.0, 0.85, 0.7) * pow(clamp(dot(n, hv), 0.0, 1.0), 40.0) * specK * sh;
  if ((hit.y > 3.5 && hit.y < 4.5) || (hit.y > 17.5 && hit.y < 18.5)) col += vec3(1.2) * pow(clamp(dot(n, normalize(vec3(-0.3, 0.4, 1.0) - rd)), 0.0, 1.0), 300.0);
  col = col / (1.0 + col * 0.25);
  col = pow(col, vec3(1.0 / 2.2));
  fragColor = vec4(col, 1.0);
}
