# ruby path
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
# jekyll path
# sudo gem install --user-install bundler jekyll
export PATH=${PATH}:/Users/colmar/.gem/ruby/3.1.0/bin

sudo gem install racc
bundle install
bundle exec jekyll build

bundle exec jekyll -v
bundle exec jekyll server

#bundle add webrick 

# By default, binaries installed by gem will be placed into:
#   /opt/homebrew/lib/ruby/gems/3.1.0/bin

# You may want to add this to your PATH.

# ruby@3.1 is keg-only, which means it was not symlinked into /opt/homebrew,
# because this is an alternate version of another formula.

# If you need to have ruby@3.1 first in your PATH, run:
#   echo 'export PATH="/opt/homebrew/opt/ruby@3.1/bin:$PATH"' >> /Users/colmar/.zshrc

# For compilers to find ruby@3.1 you may need to set:
#   export LDFLAGS="-L/opt/homebrew/opt/ruby@3.1/lib"
#   export CPPFLAGS="-I/opt/homebrew/opt/ruby@3.1/include"

# For pkgconf to find ruby@3.1 you may need to set:
#   export PKG_CONFIG_PATH="/opt/homebrew/opt/ruby@3.1/lib/pkgconfig"
