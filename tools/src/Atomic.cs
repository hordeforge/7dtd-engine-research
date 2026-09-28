// Landed-by-rename writes for every dumper output.
// A dumper target is either a committed inventory (docs/inventories/*) or a
// shared il/<set>/ tree, so writing one in place truncates a file a reader (a
// gate, an editor, git) can be holding open, and a dumper that dies mid-write
// leaves a truncated file with no rollback. Staging beside the target and
// renaming over it means a reader sees the previous file or the new one, never a
// half-written one, and a failed dump leaves the old bytes untouched.
using System.IO;

static class Atomic {
  // Staged beside the target, not in the system temp dir: a rename across
  // filesystems is a copy, and only a same-directory rename is atomic.
  private static string Staged(string path) {
    string dir = Path.GetDirectoryName(Path.GetFullPath(path));
    return Path.Combine(
      dir,
      "." + Path.GetFileName(path) + ".staged." + System.Diagnostics.Process.GetCurrentProcess().Id);
  }

  public static void WriteText(string path, string text) {
    string tmp = Staged(path);
    try {
      File.WriteAllText(tmp, text);
      Land(tmp, path);
    } catch {
      Discard(tmp);
      throw;
    }
  }

  // File.Move refuses an existing destination and File.Replace needs one, so an
  // output that is being rewritten is renamed over and a first write is moved.
  private static void Land(string tmp, string path) {
    if (File.Exists(path)) File.Replace(tmp, path, null);
    else File.Move(tmp, path);
  }

  private static void Discard(string tmp) {
    try {
      if (File.Exists(tmp)) File.Delete(tmp);
    } catch (IOException) {
      // A leftover staging file is inert: it is dot-prefixed, sits beside the
      // target, and is overwritten by the next run of the same dumper.
    }
  }
}
