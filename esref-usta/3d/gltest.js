const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  await p.setContent(`<canvas id=c width=540 height=960></canvas>`);
  const r = await p.evaluate(() => {
    const gl = document.getElementById('c').getContext('webgl2', {preserveDrawingBuffer:true});
    if (!gl) return 'no webgl2';
    const info = gl.getExtension('WEBGL_debug_renderer_info');
    const ren = info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
    const vs = `#version 300 es\nin vec2 p; void main(){gl_Position=vec4(p,0,1);}`;
    const fs = `#version 300 es\nprecision highp float; out vec4 o; uniform vec2 R;
    float map(vec3 q){ float d=1e9; for(int i=0;i<60;i++){ vec3 c=vec3(sin(float(i))*0.6,cos(float(i)*1.3)*0.9,float(i)*0.01); d=min(d,length(q-c)-0.12);} return d;}
    void main(){ vec2 uv=(gl_FragCoord.xy-0.5*R)/R.y; vec3 ro=vec3(0,0,3), rd=normalize(vec3(uv,-1.5)); float t=0.; for(int i=0;i<96;i++){ float d=map(ro+rd*t); if(d<1e-3) break; t+=d;} o=vec4(vec3(1.0/(1.0+t*0.3)),1);}`;
    function sh(t,s){const x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(x);return x;}
    const pr=gl.createProgram(); gl.attachShader(pr,sh(gl.VERTEX_SHADER,vs)); gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fs)); gl.linkProgram(pr); gl.useProgram(pr);
    const buf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buf); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
    const loc=gl.getAttribLocation(pr,'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
    gl.uniform2f(gl.getUniformLocation(pr,'R'),540,960);
    const px=new Uint8Array(4);
    const t0=performance.now(); for(let i=0;i<3;i++){ gl.drawArrays(gl.TRIANGLES,0,3); gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px);}
    return ren+' | ms/frame: '+((performance.now()-t0)/3).toFixed(0);
  });
  console.log(r); await b.close();
})();
