// Read-only recovery metadata; never print transaction input or validator config.
const address = process.argv[2];
if (!/^0x[0-9a-fA-F]{40}$/.test(address ?? '')) throw Error('Public wallet address required');
async function rpc(method, params) {
  const res = await fetch('https://studio.genlayer.com/api', {method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});
  const value = await res.json();
  if (value.error) throw Error(JSON.stringify(value.error));
  return value.result;
}
console.log(JSON.stringify({nonce:await rpc('eth_getTransactionCount',[address,'pending'])}));
const history = await rpc('sim_getTransactionsForAddress',[address]);
const transactions = Array.isArray(history)?history:history?.transactions??[];
console.log(JSON.stringify({history_keys:Object.keys(history??{}).slice(0,6),count:transactions.length,
  latest:transactions.slice(0,12).map(tx=>({hash:tx.hash??tx.tx_hash,nonce:tx.nonce,status:tx.status,
    to:tx.to_address??tx.to,type:tx.type,created:tx.created_at,
    execution:tx.consensus_data?.leader_receipt?.find(item=>item.mode==='leader')?.execution_result}))}));
