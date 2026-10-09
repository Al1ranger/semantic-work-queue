// Process-local one-shot transport for an already signed StudioNet payload.
// No key access, signing, native subprocess or automatic rebroadcast.
const {createHash} = require('node:crypto');
const original = globalThis.fetch;
const sent = new Map();
globalThis.fetch = async (url, options) => {
  let rpc;
  try { rpc=JSON.parse(options?.body??'{}'); } catch {}
  const target=new URL(String(url));
  if (target.origin!=='https://studio.genlayer.com' || target.pathname!=='/api'
      || rpc?.method!=='eth_sendRawTransaction') return original(url,options);
  if (rpc.params?.length!==1 || !/^0x[0-9a-fA-F]+$/.test(rpc.params[0])) throw Error('Invalid signed payload');
  const key=createHash('sha256').update(rpc.params[0]).digest('hex');
  if (!sent.has(key)) sent.set(key,(async()=>{
    const response=await original(url,options);
    const body=await response.text();
    let parsed;
    try { parsed=JSON.parse(body); } catch { throw Error('Broadcast result unknown; recover wallet history before resend'); }
    if (/^0x[0-9a-fA-F]{64}$/.test(parsed.result??'')) console.error(`BROADCAST_HASH ${parsed.result}`);
    return {body,status:response.status,headers:{'content-type':'application/json'}};
  })());
  const result=await sent.get(key);
  return new Response(result.body,{status:result.status,headers:result.headers});
};
