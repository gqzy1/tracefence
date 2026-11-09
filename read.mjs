import {createClient,abi} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
const config=JSON.parse(fs.readFileSync(path.join(root,'verification.json')));
const client=createClient({chain:studionet});
const chain=await client.request({method:'eth_chainId',params:[]});
if(BigInt(chain)!==61999n)throw Error('Wrong network');
const source=fs.readFileSync(path.join(root,config.source),'utf8');
if(crypto.createHash('sha256').update(source).digest('hex')!==config.source_sha256)throw Error('Source digest differs');
if(await client.getContractCode(config.address)!==source)throw Error('Deployed source differs');
for(const entry of config.transactions){
 const tx=await client.getTransaction({hash:entry.hash});
 const leader=tx.consensus_data?.leader_receipt?.at(-1);
 if((tx.status_name||tx.statusName)!=='FINALIZED'||(tx.result_name||tx.resultName)!=='MAJORITY_AGREE'||leader?.execution_result!=='SUCCESS')throw Error('Unsuccessful transaction '+entry.label);
 if(tx.leader_only!==false)throw Error('Leader-only execution');
 if((tx.from_address||tx.sender).toLowerCase()!==config.owner.toLowerCase())throw Error('Sender differs');
 if((tx.to_address||tx.recipient).toLowerCase()!==config.address.toLowerCase())throw Error('Target differs');
 const votes=Object.values(tx.consensus_data?.votes||{});
 if(!votes.includes('agree'))throw Error('No recorded agreeing validator');
 if(entry.method!=='deploy'){
  const raw=await client.request({method:'eth_getTransactionByHash',params:[entry.hash]});
  const call=Object.fromEntries(abi.calldata.decode(Buffer.from(raw.data.calldata,'base64')));
  if(call.method!==entry.method||JSON.stringify(call.args)!==JSON.stringify(entry.args))throw Error('Call binding differs');
 }
 console.log(entry.label,'FINALIZED / MAJORITY_AGREE / SUCCESS',votes.filter(x=>x==='agree').length+' agreeing votes');
}
for(const item of config.reads){
 const live=JSON.parse(await client.readContract({address:config.address,functionName:config.view,args:[config.owner,item.name],transactionHashVariant:'latest-final'}));
 const saved=JSON.parse(fs.readFileSync(path.join(root,item.file)));
 if(JSON.stringify(live)!==JSON.stringify(saved))throw Error('Finalized state differs '+item.name);
 console.log(item.name,'matches finalized state');
}
console.log('PASS: source, transactions, votes, call bindings and finalized state. No writes were sent.');
process.exit(0);

