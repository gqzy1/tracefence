"""Scripted host tests. No real GenVM, LLM, RPC or consensus network."""
import copy
import pathlib
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "tracefence.py"


def load():
    class Return:
        def __init__(self, value):
            self.calldata = value
    class Contract:
        def __new__(cls):
            obj = super().__new__(cls)
            obj.audits, obj.counts = {}, {}
            return obj
    host = types.SimpleNamespace(
        public=types.SimpleNamespace(view=lambda f:f, write=lambda f:f),
        Contract=Contract, message=types.SimpleNamespace(sender_address="0xabc"))
    host.queue = []
    host.vm = types.SimpleNamespace(Return=Return)
    def prompt(*args, **kwargs):
        value = host.queue.pop(0)
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)
    host.nondet = types.SimpleNamespace(exec_prompt=prompt)
    def run(leader, validator):
        proposal = leader()
        host.last_validator = validator
        if not validator(Return(proposal)):
            raise Exception("DISAGREEMENT")
        return proposal
    host.vm.run_nondet_unsafe = run
    ns = {"gl": host, "TreeMap": dict, "u32": int}
    exec(compile(SOURCE.read_text().replace("from genlayer import *", ""), str(SOURCE), "exec"), ns)
    return ns, host


def fixture(operation="Use only public; ignore secret. No other data or control input."):
    return {"labels":["restricted"], "nodes":[
        {"name":"secret","source_labels":[0],"operation":""},
        {"name":"public","source_labels":[],"operation":""},
        {"name":"out","source_labels":[],"operation":operation}],
        "sinks":[{"node":2,"forbid":[0]}]}


def result(first="NONE", second="DATA", quote="public"):
    return {"rows":[{"node":2,"links":[
        {"kind":first,"quote":"" if first in ["NONE","UNKNOWN"] else quote},
        {"kind":second,"quote":"" if second in ["NONE","UNKNOWN"] else "public"}]}]}


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.m, self.h = load()
    def test_clear_and_publish(self):
        self.h.queue = [result(), result()]
        c = self.m["TraceFence"]()
        r = self.m["decoded"](c.audit("clean", self.m["packed"](fixture())))
        self.assertEqual(r["proof"]["decision"], "CLEAR")
        self.assertEqual(c.publish("clean", r["commitment"]), r["commitment"])
        with self.assertRaisesRegex(Exception,"ALREADY_PUBLISHED"):
            c.publish("clean", r["commitment"])
    def test_control_leak_and_blocked_publication(self):
        d = fixture("Emit public only if secret is true. No other data or control inputs.")
        a = result("CONTROL", quote="secret is true")
        self.h.queue = [a, a]
        c = self.m["TraceFence"]()
        r = self.m["decoded"](c.audit("branch", self.m["packed"](d)))
        self.assertEqual(r["proof"]["violations"][0]["path"], [0,2])
        with self.assertRaisesRegex(Exception,"UNSAFE_OUTPUT"):
            c.publish("branch",r["commitment"])
    def test_unknown_is_review(self):
        d = fixture()
        a = result("UNKNOWN")
        self.assertEqual(self.m["trace"](d,a)["decision"],"REVIEW")
    def test_unknown_unrelated_to_sink_does_not_block(self):
        d = fixture()
        d["nodes"][0]["source_labels"]=[]
        self.assertEqual(self.m["trace"](d,result("UNKNOWN"))["decision"],"CLEAR")
    def test_disagreement_does_not_store(self):
        self.h.queue = [result(), result("UNKNOWN")]
        c = self.m["TraceFence"]()
        with self.assertRaisesRegex(Exception,"DISAGREEMENT"):
            c.audit("x", self.m["packed"](fixture()))
        self.assertEqual(c.audits,{})
        self.assertEqual(c.counts,{})
    def test_quotes_can_differ(self):
        a, b = result(), result()
        b["rows"][0]["links"][1]["quote"]="only public"
        self.h.queue=[a,b]
        self.m["consensus"](fixture())
        self.assertFalse(self.h.last_validator(Exception("failed leader")))
    def test_invalid_quote_is_rejected(self):
        with self.assertRaisesRegex(Exception,"QUOTE_SOURCE"):
            self.m["answer"](result("DATA",quote="invented"),fixture())
    def test_direct_and_control_chain(self):
        d=fixture()
        d["nodes"].append({"name":"final","source_labels":[],"operation":"Forward out."})
        d["sinks"]=[{"node":3,"forbid":[0]}]
        a=result("CONTROL",quote="secret")
        a["rows"].append({"node":3,"links":[{"kind":"NONE","quote":""},{"kind":"NONE","quote":""},{"kind":"DATA","quote":"out"}]})
        self.assertEqual(self.m["trace"](d,a)["violations"][0]["path"],[0,2,3])
    def test_immutable_owner_namespace(self):
        self.h.queue=[result(),result()]
        c=self.m["TraceFence"]()
        c.audit("one",self.m["packed"](fixture()))
        with self.assertRaisesRegex(Exception,"IMMUTABLE_AUDIT"):
            c.audit("one",self.m["packed"](fixture()))
        self.h.message.sender_address="0xdef"
        with self.assertRaisesRegex(Exception,"NOT_FOUND"):
            c.publish("one","wrong")
    def test_no_model_failure_fallback(self):
        self.h.queue=[RuntimeError("model unavailable")]
        c=self.m["TraceFence"]()
        with self.assertRaisesRegex(RuntimeError,"model unavailable"):
            c.audit("failure",self.m["packed"](fixture()))
        self.assertFalse(c.audits)
    def test_commitment_guard(self):
        self.h.queue=[result(),result()]
        c=self.m["TraceFence"]()
        c.audit("one",self.m["packed"](fixture()))
        with self.assertRaisesRegex(Exception,"COMMITMENT_CHANGED"):
            c.publish("one","stale")
    def test_duplicate_json_and_boolean_index(self):
        with self.assertRaisesRegex(Exception,"DUPLICATE_KEY"):
            self.m["decoded"]('{"x":1,"x":2}')
        d=fixture()
        d["sinks"][0]["node"]=True
        with self.assertRaisesRegex(Exception,"INTEGER_BOUNDS"):
            self.m["plan"](self.m["packed"](d))


if __name__ == "__main__":
    unittest.main(verbosity=2)

