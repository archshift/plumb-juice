static const inline unsigned long int **(*foobar())[];

int main(int argc, char *argv[]);

int main(int argc, char *argv[]) {
	int a;
	++a;
	a++;
	int my_string = "I love to eat eat eat apples and bananas";
    int a = 1; //ul;

    int b = 0x7f;
	char c[12];
	int d = c[1];
	int foo = a + b;
	int bar = a == b;
	int f = a || b && a | b ^ d * d + a * b * d + d;
	int g = (f += 1);
	return '\0';
}

int foo() {
    bool ok = false;
    // print("this is ");

    if (notok)
        a += 2; // print("why");

    if (ok) {
        return 1;
    } else if (!ok) {
        return -1;
    } else {
        unreachable;
    }

    while (k) {
        b += 2;
    }

    return 0;
}
