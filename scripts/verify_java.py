# content/alt.txt içindeki "Kod · ..." kartlarının Java çözümlerini derleyip test eder.
# Kullanım: python3 scripts/verify_java.py . [junit-standalone.jar]
# Her kartın CODE'u olduğu gibi Solution.java'ya yazılır, aşağıdaki TESTS ile Main.java üretilir.
import pathlib, re, subprocess, sys, tempfile

TESTS = {
    "HashMap ile kelime sayma": """
        Map<String, Integer> m = WordCounter.count("  Der Hund und der Ball DER");
        check(m.get("der") == 3 && m.get("hund") == 1 && m.get("ball") == 1 && m.size() == 4, m.toString());
        check(WordCounter.count("   ").isEmpty(), "bos metin");
    """,
    "ArrayList üzerinde işlem: ekle, sil, filtrele, sırala": """
        List<Student> g = StudentDemo.goodStudents();
        check(g.size() == 2 && g.get(0).name().equals("Ali") && g.get(1).name().equals("Lea"), g.toString());
    """,
    "Basit OOP modeli: Person ve Employee": """
        Person p = new Employee("Ali", 25, 2000.0);
        check(p.describe().equals("Ali (25), Gehalt: 2000.0"), p.describe());
        check(new Person("Mia", 30).describe().equals("Mia (30)"), "person");
        check(p.getName().equals("Ali"), "getName");
    """,
    "Palindrom kontrolü": """
        check(Palindrome.isPalindrome("Anna"), "Anna");
        check(Palindrome.isPalindrome("Otto"), "Otto");
        check(!Palindrome.isPalindrome("Hallo"), "Hallo");
        check(Palindrome.isPalindrome("A man, a plan, a canal: Panama"), "Panama");
        check(Palindrome.isPalindrome(""), "bos");
    """,
    "Set ile duplicate silme": """
        check(RemoveDuplicates.unique(List.of(3, 1, 3, 2, 1)).equals(List.of(3, 1, 2)), "dup");
        check(RemoveDuplicates.unique(List.of()).isEmpty(), "bos");
    """,
    "Stream API ile filtreleme: çift sayıların karesi": """
        check(EvenSquares.evenSquares(List.of(1, 2, 3, 4, 5, 6)).equals(List.of(4, 16, 36)), "even");
        check(EvenSquares.evenSquares(List.of(-2, 7)).equals(List.of(4)), "negatif");
    """,
    "Interface ve polymorphism: PaymentMethod": """
        PaymentMethod c = new CreditCard(), pp = new PayPal();
        check(c.pay(10.0).equals("10.0 EUR mit Kreditkarte bezahlt"), c.pay(10.0));
        check(pp.pay(5.5).equals("5.5 EUR mit PayPal bezahlt"), pp.pay(5.5));
        Checkout.payAll(List.of(c, pp), 20.0);
    """,
    "Exception handling: String'i sayıya çevir": """
        check(SafeParse.parseOrDefault("42", -1) == 42, "42");
        check(SafeParse.parseOrDefault(" 7 ", -1) == 7, "7");
        check(SafeParse.parseOrDefault("abc", -1) == -1, "abc");
        check(SafeParse.parseOrDefault(null, -1) == -1, "null");
        check(SafeParse.parseOrDefault("12.5", -1) == -1, "12.5");
    """,
    "Fibonacci": """
        check(Fibonacci.fib(0) == 0 && Fibonacci.fib(1) == 1 && Fibonacci.fib(2) == 1, "kucuk");
        check(Fibonacci.fib(10) == 55, "10");
        check(Fibonacci.fib(50) == 12586269025L, "50");
        try { Fibonacci.fib(-1); check(false, "negatif"); } catch (IllegalArgumentException e) { }
    """,
    "Asal sayı testi": """
        for (int n : new int[] {2, 3, 13, 97, 2147483647}) check(Prime.isPrime(n), "asal " + n);
        for (int n : new int[] {-7, 0, 1, 4, 9, 100, 2147483646}) check(!Prime.isPrime(n), "asal degil " + n);
    """,
    "Dizide max ve min bulma": """
        check(Arrays.equals(MinMax.minMax(new int[] {3, -2, 9, 4}), new int[] {-2, 9}), "minmax");
        check(Arrays.equals(MinMax.minMax(new int[] {-5, -3}), new int[] {-5, -3}), "negatif");
        check(Arrays.equals(MinMax.minMax(new int[] {5}), new int[] {5, 5}), "tek");
        try { MinMax.minMax(new int[0]); check(false, "bos"); } catch (IllegalArgumentException e) { }
    """,
    "Binary search": """
        int[] a = {1, 3, 5, 7, 9, 11};
        check(BinarySearch.search(a, 7) == 3, "7");
        check(BinarySearch.search(a, 1) == 0 && BinarySearch.search(a, 11) == 5, "uclar");
        check(BinarySearch.search(a, 4) == -1, "yok");
        check(BinarySearch.search(new int[0], 4) == -1, "bos");
    """,
    "İki sayının toplamı (Two Sum)": """
        check(Arrays.equals(TwoSum.twoSum(new int[] {2, 7, 11, 15}, 9), new int[] {0, 1}), "9");
        check(Arrays.equals(TwoSum.twoSum(new int[] {3, 2, 4}, 6), new int[] {1, 2}), "6");
        check(Arrays.equals(TwoSum.twoSum(new int[] {3, 3}, 6), new int[] {0, 1}), "33");
        check(TwoSum.twoSum(new int[] {1, 2}, 10).length == 0, "yok");
    """,
}
JUNIT = {"JUnit ile test yazma": ("CalculatorTest", 3)}

MAIN = """import java.util.*;
public class Main {
    static void check(boolean ok, String msg) { if (!ok) throw new AssertionError(msg); }
    public static void main(String[] args) {
%s
        System.out.println("OK");
    }
}
"""

def cards(text):
    for block in re.split(r"^@@ ", text, flags=re.M)[1:]:
        head, body = block.split("\n", 1)
        sec, topic, title = [x.strip() for x in head.split("|", 2)]
        if sec != "alt" or not topic.startswith("Kod"):
            continue
        m = re.search(r"^CODE:\n(.*?)(?=^(?:A|EX|SAY|HINT|SOL|PY|NOTE|WHY):)", body, re.S | re.M)
        yield title, m.group(1).rstrip() + "\n"

def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
junit = sys.argv[2] if len(sys.argv) > 2 else None
fails, seen = [], set()
for title, code in cards((root / "content" / "alt.txt").read_text()):
    seen.add(title)
    with tempfile.TemporaryDirectory() as d:
        imports = [l for l in code.splitlines() if l.startswith("import ")]
        rest = "\n".join(l for l in code.splitlines() if not l.startswith("import "))
        src = "import java.util.*;\nimport java.util.stream.*;\n" + "\n".join(imports) + "\n" + rest
        (pathlib.Path(d) / "Solution.java").write_text(src)
        if title in JUNIT:
            if not junit:
                print("SKIP (junit jar yok):", title); continue
            cls, n = JUNIT[title]
            rc, out = run(["javac", "-cp", junit, "-d", "out", "Solution.java"], d)
            if rc == 0:
                rc, out = run(["java", "-jar", junit, "-cp", "out", "--select-class", cls, "--disable-banner"], d)
                ok = re.search(r"(\d+) tests successful", out)
                if rc == 0 and (not ok or int(ok.group(1)) != n):
                    rc = 1
        elif title in TESTS:
            (pathlib.Path(d) / "Main.java").write_text(MAIN % TESTS[title])
            rc, out = run(["javac", "-d", "out", "Solution.java", "Main.java"], d)
            if rc == 0:
                rc, out = run(["java", "-ea", "-cp", "out", "Main"], d)
        else:
            rc, out = 1, "Bu kart için TESTS içinde test yok"
        print(("PASS " if rc == 0 else "FAIL ") + title)
        if rc != 0:
            print(out); fails.append(title)
missing = (set(TESTS) | set(JUNIT)) - seen
if missing:
    print("Kartı bulunamayan testler:", missing); fails += list(missing)
sys.exit(1 if fails else 0)
