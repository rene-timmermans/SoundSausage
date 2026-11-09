// Targeted static evidence export. Decompiler output is an inference, never source code.
// @category CoolEditAnalysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
import java.util.regex.Pattern;

public class FocusExport extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Pattern names = Pattern.compile(args[1]);
        Pattern strings = Pattern.compile("(?i)QueryXfm|XfmSetup|QueryCoolFilter|FilterUnderstandsFormat|^RIFF$|^sEs.$|^WAVE$|^.*\\.ses$|^XfmDo$");
        LinkedHashSet<Function> selected = new LinkedHashSet<>();
        try (PrintWriter out = new PrintWriter(new File(args[0]), "UTF-8")) {
            out.println("PROGRAM " + currentProgram.getName());
            out.println("LANGUAGE " + currentProgram.getLanguageID());
            out.println("IMAGE_BASE " + currentProgram.getImageBase());
            out.println("Static decompiler inference; no target execution.\n");
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function f = functions.next();
                if (!f.isExternal() && !f.isThunk() && names.matcher(f.getName()).find()) selected.add(f);
            }
            DataIterator data = currentProgram.getListing().getDefinedData(true);
            while (data.hasNext()) {
                Data d = data.next();
                if (!d.hasStringValue()) continue;
                String value = String.valueOf(d.getValue());
                if (!strings.matcher(value).find()) continue;
                out.println("STRING " + d.getAddress() + " " + value);
                ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(d.getAddress());
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function f = currentProgram.getFunctionManager().getFunctionContaining(ref.getFromAddress());
                    out.println("  XREF " + ref.getFromAddress() + " " + (f == null ? "<data>" : f.getName()));
                    if (f != null && selected.size() < 32) selected.add(f);
                }
            }
            DecompInterface decompiler = new DecompInterface();
            try {
                decompiler.openProgram(currentProgram);
                for (Function f : selected) {
                    monitor.checkCancelled();
                    out.println("\n=== FUNCTION " + f.getName() + " @ " + f.getEntryPoint() + " ===");
                    DecompileResults result = decompiler.decompileFunction(f, 25, monitor);
                    if (result.decompileCompleted()) {
                        String code = result.getDecompiledFunction().getC();
                        if (code.length() > 90000) {
                            out.println(code.substring(0, 90000));
                            out.println("[TRUNCATED AT 90000 CHARS]");
                        } else out.println(code);
                    } else out.println("DECOMPILATION FAILED: " + result.getErrorMessage());
                }
            } finally { decompiler.dispose(); }
            println("Exported " + selected.size() + " functions to " + args[0]);
        }
    }
}
