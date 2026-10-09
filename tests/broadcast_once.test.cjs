const test=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
test('signed payload is sent once; success and unknown failure are cached',async()=>{
  const code=fs.readFileSync('scripts/broadcast_once.cjs','utf8');
  for(const failure of [false,true]) {
    let calls=0;
    const context={require,URL,Response,console:{error(){}},fetch:async()=>{
      calls++;
      if(failure) throw Error('Unknown result');
      return new Response(JSON.stringify({result:'0x'+'a'.repeat(64)}),{status:200});
    }};
    vm.runInNewContext(code,context);
    const options={body:JSON.stringify({method:'eth_sendRawTransaction',params:['0xdeadbeef']})};
    for(let i=0;i<2;i++) {
      if(failure) await assert.rejects(context.fetch('https://studio.genlayer.com/api',options));
      else assert.equal((await context.fetch('https://studio.genlayer.com/api',options)).status,200);
    }
    assert.equal(calls,1);
  }
});
