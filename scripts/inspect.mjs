import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import crypto from 'node:crypto';
const [address, creator, id, expected] = process.argv.slice(2);
const canonical = value => value === null || typeof value !== 'object' ? JSON.stringify(value) :
  Array.isArray(value) ? `[${value.map(canonical).join(',')}]` :
    `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
const hash = value => crypto.createHash('sha256').update(canonical(value)).digest('hex');
const checkRoot = (value, field='root') => {
  const {[field]: root, ...rest} = value;
  if (hash(rest) !== root) throw Error('Root mismatch');
};
const client = createClient({chain:studionet});
const read = (functionName,args) => client.readContract({address,functionName,args});
const key = await read('job_key',[creator,id]);
const job = await read('get_job',[key]);
if (job.spec_root !== hash(job.spec) || job.spec.key !== key || job.spec.id !== id) throw Error('Job spec binding');
if (expected && job.state !== expected) throw Error(`State ${job.state} != ${expected}`);
if (Object.keys(job.report).length) {
  checkRoot(job.report);
  if (job.report.binding.job !== key || job.report.binding.spec_root !== job.spec_root) throw Error('Report binding');
  if (job.report.outcome === 'ROUTED' && (job.report.hash !== job.spec.source_hash || job.report.topic !== job.lane
      || job.report.http !== 200 || !(job.report.bytes > 0 && job.report.bytes <=16384))) throw Error('Source/lane binding');
}
if (Object.keys(job.lease).length) {
  checkRoot(job.lease,'token');
  if (job.lease.job !== key || job.lease.lane !== job.lane || job.lease.ticket !== job.ticket
      || job.lease.report_root !== job.report.root || job.lease.number !== job.leases
      || job.lease.until > job.spec.deadline) throw Error('Lease binding');
}
console.log(JSON.stringify({key,state:job.state,lane:job.lane,ticket:job.ticket,topic:job.report.topic,
  bytes:job.report.bytes,source_hash:job.report.hash,reason:job.terminal_reason,lease:job.lease,
  roots_verified:true,bindings_verified:true,...(job.lane?{queue:await read('get_lane',[job.lane])}:{})}));
